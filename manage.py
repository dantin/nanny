# -*- coding: utf-8 -*-
"""Bootstrap scripts for pinocchio robot utilities."""

import argparse
import logging
import sys

from robot import __version__
from robot.config import load_config_from_file
from robot.gym import GymBookingWorker
from robot.smh import CogentWorker
from robot.exceptions import BusinessException


LOGGER = logging.getLogger()


def print_version(args):
    print('Tools of robot, version ', __version__)


def setup_logs(file_path=''):
    """setup_logs setup logging."""
    if not file_path:
        default_handler = logging.StreamHandler(stream=sys.stdout)
    else:
        default_handler = logging.FileHandler(file_path, mode='a')
    default_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    LOGGER.addHandler(default_handler)


def parse_args():
    """parse_args parses command line arguments."""
    parser = argparse.ArgumentParser('manage.py')
    subparsers = parser.add_subparsers(help='sub-command help')

    # `gym` sub-command.
    gym_parser = subparsers.add_parser('gym', help='gym booking robot')
    gym_parser.add_argument('task', choices=('show', 'book'), default='show', help='task name')
    gym_parser.add_argument('--config', default='cfg.yml', help='path to the configuration file')
    gym_parser.add_argument('days', nargs='*', help='target days to reverse gym')
    gym_parser.add_argument('-f', '--force', help='do force reservation', action='store_true')
    gym_parser.add_argument('-l', '--log_path', default='', help='log file path')
    gym_parser.add_argument('-L', '--level', choices=('debug', 'info', 'warn'), default='info',
                            help='log level: debug, info, warn')
    gym_parser.set_defaults(func=run_gym)

    smh_parser = subparsers.add_parser('smh', help='SMH robot')
    smh_parser.add_argument('task', choices=('list',), default='list', help='task name')
    smh_parser.add_argument('--config', default='cfg.yml', help='path to the configuration file')
    smh_parser.add_argument('-l', '--log_path', default='', help='log file path')
    smh_parser.add_argument('-L', '--level', choices=('debug', 'info', 'warn'), default='info',
                            help='log level: debug, info, warn')
    smh_parser.set_defaults(func=run_smh)

    parser.add_argument('-V', '--version', help='print version info', action='store_true')
    parser.set_defaults(func=print_version)

    args = parser.parse_args()

    return args


def logger(func):
    """logger decorator sets logger level."""
    def decorator(args):
        setup_logs(args.log_path)
        level = args.level
        if level == 'debug':
            LOGGER.setLevel(logging.DEBUG)
        elif level == 'warn':
            LOGGER.setLevel(logging.WARNING)
        else:
            LOGGER.setLevel(logging.INFO)

        try:
            func(args)
        except BusinessException as e:
            LOGGER.fatal(e)

    return decorator


@logger
def run_gym(args):
    LOGGER.info('load configuration')
    cfg = load_config_from_file(args.config)

    LOGGER.info('initialize gym booking worker')
    worker = GymBookingWorker(**cfg['gym'])

    worker.execute(args.task, days=args.days, force=args.force)


@logger
def run_smh(args):
    LOGGER.info('load configuration')
    cfg = load_config_from_file(args.config)

    LOGGER.info('initialize SMH cogent worker')
    worker = CogentWorker(**cfg['smh'])

    worker.execute(args.task)


def main():
    """The main function."""
    args = parse_args()
    args.func(args)
    LOGGER.info('finish')


if __name__ == '__main__':
    main()
