import click
from .init import init
from .config import config
from .chat import chat

@click.group()
def cli():
    """Bob - AI-Assisted Software Development Tool"""
    pass

cli.add_command(init)
cli.add_command(config)
cli.add_command(chat)

__all__ = ['cli']