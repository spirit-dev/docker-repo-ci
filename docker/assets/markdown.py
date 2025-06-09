# -*- coding: utf-8 -*-
"""
Clean Repo script
"""
import argparse
import os
from jinja2 import Environment, FileSystemLoader

DEFAULT_TYPE = "github"
DEFAULT_INPUT = "template.md.j2"
DEFAULT_OUTPUT = "Readme.md"


class MdBuilder:
    """ Entry class """

    def __init__(self, repo_path, rtype, intf, outf, dr):

        self.repo_path = repo_path

        self.rtype = rtype
        if rtype is None:
            self.rtype = DEFAULT_TYPE

        self.intf = intf
        if intf is None:
            self.intf = DEFAULT_INPUT

        self.outf = outf
        if outf is None:
            self.outf = DEFAULT_OUTPUT

        self.dry_run = dr

        # Change execution location
        os.chdir(self.repo_path)

        # Summary
        print('---------------------------------------------------')
        print(f'Repo located:   {self.repo_path}')
        print(f'input:          {self.intf}')
        print(f'output:         {self.outf}')
        print(f'type:           {self.rtype}')
        print(f'Running script: {os.path.abspath(__file__)}')
        print(f'Running from:   {os.getcwd()}')
        print('')
        print('---------------------------------------------------')

        # Create a Jinja2 environment
        env = Environment(loader=FileSystemLoader(self.repo_path))

        # Load the template
        self.template = env.get_template(f'{self.intf}')

    def generate_markdown(self):

        # Render the template with the appropriate context
        context = {'repo_type': self.rtype}
        rendered_content = self.template.render(context)

        # Write the rendered content to the output file
        with open(self.outf, 'w', encoding='utf-8') as file:
            file.write(rendered_content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--repo-path')
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--type')
    parser.add_argument('--dry-run', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    md = MdBuilder(
        repo_path=args.repo_path,
        rtype=args.type,
        intf=args.input,
        outf=args.output,
        dr=args.dry_run
    )
    md.generate_markdown()
