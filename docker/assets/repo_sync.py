# -*- coding: utf-8 -*-

"""
Repository sync script
"""

# pylint: disable=line-too-long

import argparse
import subprocess
import os
import time
from urllib.parse import urlparse
import yaml


class GitLab:
    """ Entry class """

    def __init__(self, cfg_f, repo_path, dr, gl_srv_url, gl_srv_tken, gl_group, gl_uname, gl_umail):  # noqa E501
        # Local vars
        self.config_file = cfg_f
        self.repo_path = repo_path
        # Read config (yaml) file
        with open(self.repo_path + "/"+cfg_f, 'r', encoding="utf-8") as file:  # noqa: E501
            config = yaml.safe_load(file)
        os.remove(self.repo_path + "/"+cfg_f)
        # Dry run
        self.dry_run = dr
        self.repo_local_name = config['repo_local_name']

        # GitLab vars
        self.ci_server_url = self.set_var_env(gl_srv_url, 'CI_SERVER_URL')
        server_token = self.set_var_env(gl_srv_tken, 'CI_SERVER_TOKEN')
        self.gitlab_group = self.set_var_env(gl_group, 'GL_DEFAULT_GROUP')
        self.gitlab_user_name = self.set_var_env(gl_uname, 'GL_USER_NAME')
        self.gitlab_user_mail = self.set_var_env(gl_umail, 'GL_USER_MAIL')
        self.gitlab_sync_repo_name = self.set_var_conf(
            config['repo_local_name'], 'gitlab_sync_repo_name', config)
        # GitLab Url
        o = urlparse(self.ci_server_url)
        self.gl_url = f"{o.scheme}://oauth2:{server_token}@{o.netloc}/{self.gitlab_group}/{self.gitlab_sync_repo_name}.git"  # noqa E501
        self.gl_url_mask = f"{o.scheme}://oauth2:******@{o.netloc}/{self.gitlab_group}/{self.gitlab_sync_repo_name}.git"  # noqa E501
        self.gl_ori_url = f"{o.scheme}://oauth2:{server_token}@{o.netloc}/{os.environ['CI_PROJECT_PATH']}"  # noqa E501

        # Change execution location
        os.chdir(self.repo_path)
        self.pwd = os.getcwd()

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
        print('Git url:        '+self.gl_url_mask)
        print('')
        print('Repo located:   '+self.pwd)
        print('Config file:    '+self.config_file)
        print('Running from:   '+os.path.abspath(__file__))
        print('')
        print('Server host:    '+self.ci_server_url)
        print('---------------------------------------------------')

        print('Repository:    '+self.repo_local_name)

        # Set path safe
        # git config --global --add safe.directory $(pwd)
        print('\tSafe space')
        subprocess.Popen(['git', 'config',
                          '--global', '--add',
                          'safe.directory', self.pwd])
        time.sleep(5)

        # git status
        print('\tstatus')
        subprocess.Popen(['git', 'status'])
        time.sleep(5)

        # Set user
        print('\tset user')
        # git config user.email $GL_USER_MAIL
        subprocess.Popen([
            'git', 'config', 'user.email',
            self.gitlab_user_mail
        ])
        # git config user.name $GL_USER_NAME
        subprocess.Popen([
            'git', 'config', 'user.name',
            self.gitlab_user_name
        ])
        time.sleep(5)

        # GIt commit
        print('\tcommit')
        # git add .
        subprocess.Popen(['git', 'add', '.'])
        time.sleep(5)
        # git commit -m 'synced by ci bot'
        subprocess.Popen(['git', 'commit', '-m', 'synced by ci bot'])
        time.sleep(5)

        # Git fetch
        # git fetch --unshallow https://oauth2:$CI_SERVER_TOKEN@$CI_SERVER_HOST/$CI_PROJECT_PATH # noqa E501
        subprocess.Popen(["git", "fetch", "--unshallow", self.gl_ori_url])
        time.sleep(5)
        # git init
        subprocess.Popen(["git", "init"])
        time.sleep(5)
        # Change remote
        print('\tremote add')
        subprocess.Popen(['git', 'remote',
                          'add', 'origin_gl',
                          self.gl_url])
        time.sleep(5)
        # git push origin master
        print('\tpush')
        subprocess.Popen(
            ["git", "push", "--force", "origin_gl", "HEAD:refs/heads/main"])
        time.sleep(5)


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
    parser.add_argument('--gitlab-user-name')
    parser.add_argument('--gitlab-user-mail')

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
        gl_uname=args.gitlab_user_name,
        gl_umail=args.gitlab_user_mail,
    )
    glab.exec()
