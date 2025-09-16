#!/usr/bin/env python3
"""
GitLab Merge Request Comment Poster
Sends comments to GitLab merge requests via API
"""

import os
import sys
import argparse
from typing import Optional
import requests


class GitLabMRCommenter:
    """
    Class responsible to create a comment in MRs
    """

    def __init__(self):
        self.api_url = os.environ.get(
            'GITLAB_API_URL',
            os.environ.get('CI_API_V4_URL')
        )
        self.project_id = os.environ.get('CI_PROJECT_ID')
        self.ci_commit_ref_name = os.environ.get('CI_COMMIT_REF_NAME')
        self.token = os.environ.get('RENOVATE_TOKEN')
        self.mr_iid = None  # Will be fetched dynamically

        required_vars = [
            self.api_url, self.project_id,
            self.ci_commit_ref_name, self.token
        ]

        if not all(required_vars):
            missing = []
            if not self.api_url:
                missing.append('GITLAB_API_URL or CI_API_V4_URL')
            if not self.project_id:
                missing.append('CI_PROJECT_ID')
            if not self.ci_commit_ref_name:
                missing.append('CI_COMMIT_REF_NAME')
            if not self.token:
                missing.append('RENOVATE_TOKEN')

            error_msg = f"Missing required environment variables: {', '.join(missing)}" # noqa E501
            raise ValueError(error_msg)

    def _get_mr_iid(self) -> Optional[int]:
        """
        Find the MR IID for the current branch by querying GitLab API

        Returns:
            int: MR IID if found, None otherwise
        """
        if self.mr_iid is not None:
            return self.mr_iid

        url = f"{self.api_url}/projects/{self.project_id}/merge_requests"
        params = {
            'scope': 'all',
            'state': 'opened',
            'source_branch': self.ci_commit_ref_name
        }

        headers = {
            'PRIVATE-TOKEN': self.token,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=30
            )
            response.raise_for_status()

            merge_requests = response.json()

            if not merge_requests:
                warning_msg = (
                    f"⚠️ No open merge requests found for branch "
                    f"'{self.ci_commit_ref_name}'"
                )
                print(warning_msg, file=sys.stderr)
                return None

            if len(merge_requests) > 1:
                warning_msg = (
                    f"⚠️ Multiple merge requests found for branch "
                    f"'{self.ci_commit_ref_name}', using the first one"
                )
                print(warning_msg, file=sys.stderr)

            mr_iid = merge_requests[0]['iid']
            self.mr_iid = mr_iid  # Cache the result
            success_msg = (
                f"📝 Found merge request !{mr_iid} for branch "
                f"'{self.ci_commit_ref_name}'"
            )
            print(success_msg)

            return mr_iid

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch merge request IID: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}", file=sys.stderr)
            return None

    def post_comment(self, comment: str) -> bool: # noqa E501
        """
        Post a comment to the merge request

        Args:
            comment: The comment content (markdown supported)

        Returns:
            bool: True if successful, False otherwise
        """
        mr_iid = self._get_mr_iid()
        if mr_iid is None:
            print(
                "❌ Cannot post comment: No merge request found",
                file=sys.stderr
            )
            return False

        url = (
            f"{self.api_url}/projects/{self.project_id}/"
            f"merge_requests/{mr_iid}/notes"
        )

        headers = {
            'PRIVATE-TOKEN': self.token,
            'Content-Type': 'application/json'
        }

        data = {
            'body': comment
        }

        try:
            response = requests.post(
                url, headers=headers, json=data, timeout=30
            )
            response.raise_for_status()

            print(f"✅ Comment posted successfully to MR !{mr_iid}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to post comment: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}", file=sys.stderr)
            return False

    def update_or_create_comment(self, comment: str, identifier: str) -> bool:
        """
        Update existing comment with identifier or create new one

        Args:
            comment: The comment content
            identifier: Unique identifier to find existing comment

        Returns:
            bool: True if successful, False otherwise
        """
        # Add identifier to comment
        comment_with_id = f"<!-- {identifier} -->\n{comment}"

        # Try to find existing comment
        existing_note_id = self._find_existing_note(identifier)

        if existing_note_id:
            return self._update_note(existing_note_id, comment_with_id)
        else:
            return self.post_comment(comment_with_id)

    def _find_existing_note(self, identifier: str) -> Optional[int]:
        """Find existing note with identifier"""
        mr_iid = self._get_mr_iid()
        if mr_iid is None:
            return None

        url = (
            f"{self.api_url}/projects/{self.project_id}/"
            f"merge_requests/{mr_iid}/notes"
        )

        headers = {
            'PRIVATE-TOKEN': self.token,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            notes = response.json()
            for note in notes:
                if f"<!-- {identifier} -->" in note.get('body', ''):
                    return note['id']

            return None

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed to fetch existing notes: {e}", file=sys.stderr)
            return None

    def _update_note(self, note_id: int, comment: str) -> bool:
        """Update existing note"""
        mr_iid = self._get_mr_iid()
        if mr_iid is None:
            return False

        url = (
            f"{self.api_url}/projects/{self.project_id}/"
            f"merge_requests/{mr_iid}/notes/{note_id}"
        )

        headers = {
            'PRIVATE-TOKEN': self.token,
            'Content-Type': 'application/json'
        }

        data = {
            'body': comment
        }

        try:
            response = requests.put(
                url, headers=headers, json=data, timeout=30
            )
            response.raise_for_status()

            print(f"✅ Comment updated successfully in MR !{mr_iid}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to update comment: {e}", file=sys.stderr)
            return False


def create_helm_diff_comment(
    added_lines: int,
    removed_lines: int,
    diff_content: str,
    branch_name: str,
    pipeline_url: str,
    job_id: str,
    max_diff_size: int = 45000
) -> str:
    """Create formatted helm diff comment"""

    if added_lines == 0 and removed_lines == 0:
        return f"""## 🎯 Helm Chart Diff Results

✅ **No differences found** between `main` and `{branch_name}` branches.

The Helm chart templates are identical - no resources will be changed by this merge request."""

    # Truncate diff if too large
    if len(diff_content) > max_diff_size:
        truncated_diff = diff_content[:max_diff_size]
        diff_display = f"""{truncated_diff}

... (diff truncated - total size: {len(diff_content)} characters)
📎 **Full diff available in pipeline artifacts**"""
    else:
        diff_display = diff_content

    artifact_url = f"{pipeline_url}/-/jobs/{job_id}/artifacts/download"

    return f"""## 🎯 Helm Chart Diff Results

📊 **Changes detected** between `main` and `{branch_name}` branches:
- **{added_lines}** lines added
- **{removed_lines}** lines removed

<details>
<summary>📋 Click to view the diff</summary>

```diff
{diff_display}
```

</details>

💡 **Review the changes above** to understand the impact on your Kubernetes resources.
🔗 [View full pipeline logs]({pipeline_url}) | 📎 [Download diff artifact]({artifact_url})"""


def main():
    """
    main entrypoint
    """

    parser = argparse.ArgumentParser(
        description='Post comment to GitLab Merge Request'
    )
    parser.add_argument(
        '--comment', '-c',
        help='Comment text (or read from stdin)'
    )
    parser.add_argument(
        '--file', '-f',
        help='Read comment from file'
    )
    parser.add_argument(
        '--identifier', '-i',
        help='Unique identifier for updating existing comments'
    )
    parser.add_argument(
        '--helm-diff',
        action='store_true',
        help='Create helm diff comment'
    )
    parser.add_argument(
        '--added-lines',
        type=int,
        default=0,
        help='Number of added lines (for helm diff)'
    )
    parser.add_argument(
        '--removed-lines',
        type=int,
        default=0,
        help='Number of removed lines (for helm diff)'
    )
    parser.add_argument(
        '--diff-file',
        help='File containing diff content (for helm diff)'
    )
    parser.add_argument(
        '--branch-name',
        help='Branch name (defaults to CI_COMMIT_REF_NAME)'
    )
    parser.add_argument(
        '--pipeline-url',
        help='Pipeline URL (defaults to CI_PIPELINE_URL)'
    )
    parser.add_argument(
        '--job-id',
        help='Job ID (defaults to CI_JOB_ID)'
    )

    args = parser.parse_args()

    try:
        commenter = GitLabMRCommenter()

        if args.helm_diff:
            # Create helm diff comment
            branch_name = (
                args.branch_name or
                os.environ.get('CI_COMMIT_REF_NAME', 'unknown')
            )
            pipeline_url = (
                args.pipeline_url or
                os.environ.get('CI_PIPELINE_URL', '')
            )
            job_id = args.job_id or os.environ.get('CI_JOB_ID', '')

            diff_content = ""
            if args.diff_file and os.path.exists(args.diff_file):
                with open(args.diff_file, 'r') as f:
                    diff_content = f.read()

            comment = create_helm_diff_comment(
                args.added_lines, args.removed_lines, diff_content,
                branch_name, pipeline_url, job_id
            )

            identifier = args.identifier or "helm-chart-diff"
            success = commenter.update_or_create_comment(comment, identifier)

        else:
            # Regular comment
            if args.file:
                with open(args.file, 'r') as f:
                    comment = f.read()
            elif args.comment:
                comment = args.comment
            else:
                comment = sys.stdin.read()

            if args.identifier:
                success = commenter.update_or_create_comment(
                    comment, args.identifier
                )
            else:
                success = commenter.post_comment(comment)

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
