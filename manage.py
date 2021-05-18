# -*- coding: utf-8 -*-
"""Bootstrap scripts."""
import logging

import click
from colorama import Fore, Style


logger = logging.getLogger(__name__)


def init() -> None:
    """init do app initialization."""
    from nanny.utils.logger_configurator import DefaultLoggingConfigurator

    logging_configurator = DefaultLoggingConfigurator()
    logging_configurator.configure_logging(True)


def normalize_token(token_name: str) -> str:
    return token_name.replace('_', '-')


@click.group(
    context_settings={'token_normalize_func': normalize_token},
)
def cli() -> None:
    """This is a management script for running daily task automatic utilities."""
    pass


@cli.command()
@click.option('--days', '-d', default=7, help='Time range in days.')
def book_gym(days: int) -> None:
    """Book gymnasium."""
    from nanny.gym import GymBooker

    bot = GymBooker()
    bot.reserve(days)


@cli.command()
def show_gym() -> None:
    """Show reserved gymnasium."""
    from nanny.gym import GymBooker

    bot = GymBooker()
    bot.show()


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Show extra information.')
def version(verbose: bool) -> None:
    """Print version number."""
    from nanny import __version__ as version
    print(Fore.BLUE + '==' * 23)
    print(
        Fore.YELLOW + f'Nanny {version}'
    )
    print(Fore.BLUE + '==' * 23)
    print(Style.RESET_ALL)


if __name__ == '__main__':
    init()
    cli()
