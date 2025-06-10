# -*- coding: utf-8 -*-

"""
Clean Repo script
"""

# pylint: disable=line-too-long

import argparse
import subprocess
import os
import yaml


class RepositoryCleaner:
    """ Entry class """

    def __init__(self, config_file, repo_path, dr):
        self.config_file = config_file
        self.repo_path = repo_path
        self.dry_run = dr
        self.reports_path = f"{self.repo_path}/reports"
        self.reports_file1 = "git-filter-branch.txt"
        self.reports_file2 = "git-filter-repo.txt"

    def exec(self):
        """ main function """

        # Read config (yaml) file
        with open(self.repo_path + "/"+self.config_file, 'r', encoding="utf-8") as file:  # noqa: E501
            config = yaml.safe_load(file)

        # Grab parameters
        repo_local_name = config['repo_local_name']
        exclusion_files = config['exclusion_files']

        # Change execution location
        os.chdir(self.repo_path)

        # Summary
        print('---------------------------------------------------')
        print('Cleaning up repo: '+repo_local_name)
        print('Repo located:     '+self.repo_path)
        print('Config file:      '+self.config_file)
        print('')
        print('Running from:     '+os.path.abspath(__file__))
        print('---------------------------------------------------')

        # Set path safe
        self.safe_directory(self.repo_path)

        # Create reports dir if not exists
        if not os.path.exists(self.reports_path):
            os.makedirs(self.reports_path)

        # Execute filters
        for excl in exclusion_files:

            # Execute git filter-branch
            print('git filter-branch - Deleting from repo: '+excl)
            if not self.dry_run:
                self.filter_branch(excl)
            else:
                print("dry-run")

            # Execute git filter-repo
            print('git filter-repo - Deleting from repo: '+excl)
            if not self.dry_run:
                self.filter_repo(excl)
            else:
                print("dry-run")

    def safe_directory(self, repodir):
        """
        Generate global safe repo (gitconfig file)

        Args:
            repodir (str): Repository path
        """
        subprocess.Popen(['git', 'config',
                          '--global', '--add',
                          'safe.directory', repodir])

    def filter_branch(self, loc):
        """Execute branch filtering

        Args:
            loc (str): file location to remove from history

        Returns:
            obj: process response
        """
        # removes object at location from all commits and tags
        subcommand = f"'git rm -rf --cached --ignore-unmatch {loc}'"
        with open("{}/{}".format(self.reports_path, self.reports_file1), "a", encoding="utf-8") as fout:  # noqa: E501
            # don't use pipe or it will deadlock when the buffer fills up
            p = subprocess.Popen(' '.join(
                [
                    'git',
                    'filter-branch',
                    '-f',
                    '--index-filter',
                    subcommand,
                    '--tag-name-filter',
                    'cat', '--',
                    '--all'
                ]
            ), stdout=fout, stderr=fout, shell=True)
            # p = subprocess.Popen(' '.join(['git', 'filter-branch', '-f',
            #                                '--index-filter', subcommand,
            #                                'HEAD']),
            #                      stdout=fout, stderr=fout, shell=True)

            # git filter-branch --index-filter 'git rm -rf --cached --ignore-unmatch path_to_file' HEAD # noqa: E501
        p.wait()
        return p

    def filter_repo(self, loc):
        """Execute repo filtering

        Args:
            loc (str): file location to remove from history

        Returns:
            obj: process response
        """
        # removes object from all commits and tags using git filter-repo
        with open("{}/{}".format(self.reports_path, self.reports_file2), "a", encoding="utf-8") as fout:  # noqa: E501
            # don't use pipe or it will deadlock when the buffer fills up
            p = subprocess.Popen(' '.join(['git', 'filter-repo',
                                           '--invert-paths',
                                           '--force',
                                           '--path', loc]),
                                 stdout=fout, stderr=fout, shell=True)
            # git filter-repo --invert-paths --path <path to the file or directory> # noqa: E501
        p.wait()
        return p


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--config-file')
    parser.add_argument('--repo-path')
    parser.add_argument('--dry-run', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    repo_cleaner = RepositoryCleaner(
        config_file=args.config_file, repo_path=args.repo_path, dr=args.dry_run)  # noqa: E501
    repo_cleaner.exec()
