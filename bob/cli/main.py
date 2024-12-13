import click
from .init import init

@click.group()
def cli():
    """Bob - AI-Assisted Software Development Tool"""
    pass

cli.add_command(init)

# Explicitly export the cli function
__all__ = ['cli']