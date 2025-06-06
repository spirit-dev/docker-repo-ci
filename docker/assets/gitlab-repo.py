# -*- coding: utf-8 -*-
"""
Clean Repo script
"""
import argparse
import os
from urllib.parse import urlparse
import yaml
import gitlab


class GitLab:
    """ Entry class """

    def __init__(self, cfg_f, repo_path, dr, gl_srv_url, gl_srv_tken, gl_group, gl_c_repo, gl_c_mirr, gh_user, gh_pass, gh_org):
        # Local vars
        self.config_file = cfg_f
        self.repo_path = repo_path
        # Read config (yaml) file
        with open(self.repo_path + "/"+self.config_file, 'r', encoding="utf-8") as file:  # noqa: E501
            config = yaml.safe_load(file)
        # Dry run
        self.dry_run = dr
        self.repo_local_name = config['repo_local_name']

        # GitLab vars
        self.ci_server_url = self.set_var_env(gl_srv_url, 'CI_SERVER_URL')
        server_token = self.set_var_env(gl_srv_tken, 'CI_SERVER_TOKEN')
        self.gitlab_group = self.set_var_env(gl_group, 'GL_DEFAULT_GROUP')
        self.gitlab_sync_repo_name = self.set_var_conf(
            config['repo_local_name'], 'gitlab_sync_repo_name', config)
        self.gitlab_sync_repo_desc = self.set_var_conf(
            "", 'gitlab_sync_repo_desc', config)
        self.gl_c_repo = self.set_var_conf(
            gl_c_repo, 'gitlab_create_repo', config)
        self.gl_c_mirr = self.set_var_conf(
            gl_c_mirr, 'gitlab_create_mirror', config)

        # GitHub vars
        gh_user = self.set_var_env(gh_user, 'GITHUB_USER')
        gh_pass = self.set_var_env(gh_pass, 'GITHUB_PASS')
        org_name = self.set_var_env(gh_org, 'GITHUB_ORG')
        self.github_repo_name = config['github_repo_name']
        # Github URLs
        domain = "github.com"
        self.gh_r_url_final = f"https://{gh_user}:{gh_pass}@{domain}/{org_name}/{self.github_repo_name}.git"
        self.gh_r_url_mask = f"https://*****:*****@{domain}/{org_name}/{self.github_repo_name}.git"

        # private token or personal token authentication (self-hosted GitLab instance)
        self.gl = gitlab.Gitlab(
            self.ci_server_url,
            private_token=server_token,
            user_agent='repo-ci/1.0.0'
        )
        # self.gl.enable_debug()

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
        print('GitLab group:   '+self.gitlab_group)
        print('')
        print('Repo located:   '+self.repo_path)
        print('Config file:    '+self.config_file)
        print('Running from:   '+os.path.abspath(__file__))
        print('')
        print('Server host:    '+self.ci_server_url)
        print('---------------------------------------------------')

        print('Repository:    '+self.repo_local_name)
        # Get repo (attempt)
        repo = self.get_repo(self.gitlab_sync_repo_name)
        # If no repo found, create one
        if (repo is None and self.gl_c_repo) and not self.dry_run:
            repo = self.create_repo(
                self.gitlab_sync_repo_name,
                self.gitlab_sync_repo_desc,
                self.gitlab_group)
        else:
            if self.dry_run:
                print("\tRepo create skipped: dry-run")
            if not self.gl_c_repo:
                print("\tRepo create skipped: creation disabled")
            if repo is not None:
                print("\tRepo already exists")

        # Create mirror
        print('Mirror in:     '+self.repo_local_name)
        if repo is not None:
            mirror = self.get_mirror(repo)
        else:
            mirror = None
        if ((repo is not None and mirror is None) and self.gl_c_mirr) and not self.dry_run:
            mirror = self.create_mirror(repo)
        else:
            if self.dry_run:
                print('\tMirror create skipped: dry-run')
            if not self.gl_c_mirr:
                print('\tMirror create skipped: creation disabled')
            if mirror is not None:
                print("\tMirror already created")

    def get_mirror(self, repo):
        """
        find and returns mirror based on its target

        Args:
            repo (object): repository

        Returns:
            object: mirror
        """
        print(f"\tGet repo mirror {self.gh_r_url_mask}")
        for mirror in repo.remote_mirrors.list(get_all=True):
            if mirror.url == self.gh_r_url_mask:
                return mirror
        return None

    def create_mirror(self, repo):
        """
        Creates and return a mirror

        Args:
            repo (object): repository

        Returns:
            object: mirror
        """
        print(
            f"\tCreate mirror {self.gh_r_url_mask} in repo {repo.name}")
        mirror = repo.remote_mirrors.create({
            'url': self.gh_r_url_final,
            'enabled': True,
            'only_protected_branches': True,
            'auth_method': 'password',
        })
        print("\t\ty")
        return mirror

    def create_repo(self, repo, desc, group):
        """
        Creates and returns a repository

        Args:
            repo (str): repository name
            desc (str): repository desciption
            group (str): group name where to create

        Returns:
            object: repository
        """
        print(f"\tCreate repo {group} / {repo}")
        group_id = self.gl.groups.list(search=group, get_all=False)[0].id
        repo = self.gl.projects.create(
            {'name': repo, 'namespace_id': group_id, 'description': desc})
        print("\t\ty")
        return repo

    def get_repo(self, name: str):
        """
        Finds and return a repository

        Args:
            name (str): repository name

        Returns:
            obejct: repository
        """
        print(f"\tGet repo {name}")
        for project in self.gl.projects.list(get_all=True):
            if project.name == name:
                return project

        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Local args
    parser.add_argument('--config-file')
    parser.add_argument('--repo-path')
    parser.add_argument('--dry-run', action=argparse.BooleanOptionalAction)
    # Gitlab args
    parser.add_argument('--gitlab-server')
    parser.add_argument('--gitlab-server-token')
    parser.add_argument('--gitlab-group')
    parser.add_argument('--gitlab-create-repo',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--gitlab-create-mirror',
                        action=argparse.BooleanOptionalAction)
    # Github args
    parser.add_argument('--github-user')
    parser.add_argument('--github-pass')
    parser.add_argument('--github-org')

    args = parser.parse_args()

    glab = GitLab(
        # Local args
        cfg_f=args.config_file,
        repo_path=args.repo_path,
        dr=args.dry_run,
        # GitLab args
        gl_srv_url=args.gitlab_server,
        gl_srv_tken=args.gitlab_server_token,
        gl_group=args.gitlab_group,
        gl_c_repo=args.gitlab_create_repo,
        gl_c_mirr=args.gitlab_create_mirror,
        # GitHub args
        gh_user=args.github_user,
        gh_pass=args.github_pass,
        gh_org=args.github_org,
    )
    glab.exec()
