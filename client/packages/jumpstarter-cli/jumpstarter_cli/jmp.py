"""Main jmp CLI command."""

import click


@click.group()
@click.option("--log-level", default="INFO", help="Set the logging level")
def jmp(log_level):
    """The Jumpstarter CLI for device automation and testing."""
    pass


@jmp.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"jumpstarter-cli version {__version__}")


@jmp.command()
@click.option("--server", default="localhost:8080", help="Jumpstarter server address")
def login(server):
    """Login to a Jumpstarter server."""
    click.echo(f"Logging in to {server}...")
    click.echo("Note: This is a basic implementation. Full client integration coming soon.")


@jmp.command()
def config():
    """Show configuration."""
    click.echo("Configuration management coming soon.")


@jmp.command()
def get():
    """Get resources from the server."""
    click.echo("Resource listing coming soon.")


if __name__ == "__main__":
    jmp()