import click
from .init import init
from .config import config
from .chat import chat
from .objectives import objectives
from .user_stories import user_stories
from .design import design

@click.group()
def cli():
    """Bob - AI-Assisted Software Development Tool"""
    pass

cli.add_command(init)
cli.add_command(config)
cli.add_command(chat)
cli.add_command(objectives)
cli.add_command(user_stories)
cli.add_command(design)

__all__ = ['cli']