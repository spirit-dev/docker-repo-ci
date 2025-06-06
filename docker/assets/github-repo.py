# -*- coding: utf-8 -*-
"""
GitHub Repo script
"""
import argparse
import os
import sys
import yaml
from github import Github, Auth


class GitLab:
    """ Entry class """

    def __init__(self, cfg_f, repo_path, dr, gh_user, gh_pass, gh_org, gh_c_repo):
        # Local vars
        self.config_file = cfg_f
        self.repo_path = repo_path
        # Read config (yaml) file
        with open(self.repo_path + "/"+self.config_file, 'r', encoding="utf-8") as file:  # noqa: E501
            config = yaml.safe_load(file)
        # Dry run
        self.dry_run = dr
        self.repo_local_name = config['repo_local_name']

        # GitHub vars
        gh_user = self.set_var_env(gh_user, 'GITHUB_USER')
        gh_pass = self.set_var_env(gh_pass, 'GITHUB_PASS')
        self.github_org_name = self.set_var_env(gh_org, 'GITHUB_ORG')
        self.github_repo_name = config['github_repo_name']
        self.github_repo_description = self.set_var_conf(
            "", 'gitlab_sync_repo_desc', config)
        self.gh_c_repo = self.set_var_conf(
            gh_c_repo, 'github_create_repo', config)
        # GH object using an access token
        auth = Auth.Token(gh_pass)
        self.gh = Github(auth=auth)

        # Change execution location
        os.chdir(self.repo_path)

    def set_var_conf(self, var, key, config):
        """
        Facilitate config set up

        Args:
            var (str): input var
            key (str): key in config
            config (object): config key-values

        Returns:
            str: computed var to use
        """
        ret = var
        if key in config:
            ret = config[key]
        return ret

    def set_var_env(self, var, env):
        """
        Function to facilitate env vars

        Args:
            var (str): input value
            env (str): env key to check

        Returns:
            str: computed env var to use
        """
        ret = var
        if var is None:
            ret = os.environ[env]
        return ret

    def exec(self):
        """ main function """

        # Summary
        print('---------------------------------------------------')
        print('Gitlab repo:    '+self.repo_local_name)
        print('GitHub repo:    '+self.github_repo_name)
        print('')
        print('Repo located:   '+self.repo_path)
        print('Config file:    '+self.config_file)
        print('Running from:   '+os.path.abspath(__file__))
        print('')
        print('---------------------------------------------------')

        print('Repository:    '+self.repo_local_name)
        # Get org
        org = self.get_org(self.github_org_name)
        # Get repo (attempt)
        repo = self.get_repo(org, self.github_repo_name)
        # If no repo found, create one
        if (repo is None and self.gh_c_repo) and not self.dry_run:
            repo = self.create_repo(org)
        else:
            if self.dry_run:
                print("\tRepo create skipped: dry-run")
            if not self.gh_c_repo:
                print("\tRepo create skipped: creation disabled")
            if repo is not None:
                print("\tRepo already exists")

        # Ensure branch ruleset
        print('Branch ruleset enforcement')
        b = repo.get_branch("main")
        b.edit_protection(
            strict=True,
            dismiss_stale_reviews=True,
            require_code_owner_reviews=True,
            required_approving_review_count=1,
            allow_force_pushes=False,
            allow_deletions=False,
            block_creations=False,
            users_bypass_pull_request_allowances=['jbordat-jb'],
            user_push_restrictions=['jbordat-jb'],
        )

        # TODO Ensure webhook

        # To close connections after use
        self.gh.close()

    def create_repo(self, org):
        """
        Create repository

        Args:
            org (object): organization

        Returns:
            object: created repository
        """
        print(f"\tCreate repo {self.github_repo_name}")
        repo = org.create_repo(
            name=self.github_repo_name,
            description=self.github_repo_description,
        )
        print("\t\ty")
        return repo

    def get_repo(self, org, name: str):
        """
        Find and return repository based on its name

        Args:
            org (object): organization
            name (str): repository name

        Returns:
            object: repository
        """
        print(f"\tGet repo {name}")
        repos = org.get_repos()
        for repo in repos:
            if repo.name == name:
                return repo

        return None

    def get_org(self, org_name):
        """
        Find and returns the organization (spirit-dev)

        Args:
            org_name (str): organization name

        Returns:
            object: organization
        """
        print(f"\tGet org {org_name}")
        return self.gh.get_organization(org_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Local args
    parser.add_argument('--config-file')
    parser.add_argument('--repo-path')
    parser.add_argument('--dry-run', action=argparse.BooleanOptionalAction)
    # Github args
    parser.add_argument('--github-user')
    parser.add_argument('--github-pass')
    parser.add_argument('--github-org')
    parser.add_argument('--github-create-repo',
                        action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    glab = GitLab(
        # Local args
        cfg_f=args.config_file,
        repo_path=args.repo_path,
        dr=args.dry_run,
        # GitHub args
        gh_user=args.github_user,
        gh_pass=args.github_pass,
        gh_org=args.github_org,
        gh_c_repo=args.github_create_repo,
    )
    glab.exec()
