import argparse
import os
import subprocess # nosec

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(dest='command', required=True)
        compile_parser = subparsers.add_parser('compile')
        compile_parser.add_argument(
            '--watch', action='store_true',
            help='Watch scripts and recompile when they change.',
        )

    def handle(self, *args, **options):
        if options['command'] == 'compile':
            self.compile(*args, **options)

    def compile(self, watch, *args, **options):
        static_directory = settings.STATICFILES_DIRS[0]
        command = [
            'yarn',
            'run',
            'tsc',
            '--project',
            os.path.join(static_directory, 'ts', 'tsconfig.compile.json'),
        ]

        if watch:
            command += ['--watch']

        try:
            subprocess.run(command, check=True) # nosec
        except FileNotFoundError:
            print('Could not find tsc command', file=self.stderr)
        except KeyboardInterrupt:
            pass
        except subprocess.CalledProcessError:
            pass
