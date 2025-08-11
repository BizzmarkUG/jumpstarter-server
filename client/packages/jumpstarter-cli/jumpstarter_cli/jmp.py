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
    click.echo(f"Connecting to jumpstarter server at {server}...")

    # Basic connectivity test
    import socket

    try:
        host, port_str = server.split(":")
        port = int(port_str)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            click.echo(f"✓ Successfully connected to {server}")
            click.echo("Note: Authentication and full gRPC integration coming soon.")
        else:
            click.echo(f"✗ Could not connect to {server}")
            click.echo("Make sure the jumpstarter standalone server is running:")
            click.echo("  docker-compose up -d")
            click.echo("  # or")
            click.echo("  go run cmd/standalone/main.go --config /tmp/jumpstarter/config.yaml")
    except Exception as e:
        click.echo(f"✗ Connection failed: {e}")
        click.echo("Please check the server address and ensure the server is running.")


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
