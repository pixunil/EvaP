import argparse
import os
import subprocess # nosec
import unittest

from django.core.management.base import BaseCommand
from django.conf import settings
from django.test.runner import DiscoverRunner


class ExportRunner(DiscoverRunner):
    test_loader = unittest.TestLoader()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_loader.testMethodPrefix = 'generate_fixtures'


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(dest='command', required=True)
        compile_parser = subparsers.add_parser('compile')
        compile_parser.add_argument(
            '--watch', action='store_true',
            help='Watch scripts and recompile when they change.',
        )
        test_parser = subparsers.add_parser('test')
        generate_fixtures_parser = subparsers.add_parser('generate_fixtures')

    def handle(self, *args, **options):
        if options['command'] == 'compile':
            self.compile(*args, **options)
        elif options['command'] == 'test':
            self.test(*args, **options)
        elif options['command'] == 'generate_fixtures':
            self.generate_fixtures(*args, **options)

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

    def test(self, *args, **options):
        command = [
            'yarn',
            'run',
            'jest',
        ]

        try:
            subprocess.run(command, check=True) # nosec
        except KeyboardInterrupt:
            pass

    def generate_fixtures(self, *args, **options):
        # Enable debug mode as otherwise a collectstatic beforehand would be necessary
        test_runner = ExportRunner(keepdb=True, debug_mode=True)
        test_runner.run_tests([])
