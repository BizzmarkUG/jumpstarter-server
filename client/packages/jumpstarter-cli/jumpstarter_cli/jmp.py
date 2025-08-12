"""Main jmp CLI command."""

import click


# Simplified AliasedGroup for standalone mode
class AliasedGroup(click.Group):
    """Allow command aliases."""
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        
        # Try to find a command that starts with the given name
        matches = [cmd for cmd in self.list_commands(ctx) 
                  if cmd.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")


@click.group(cls=AliasedGroup)
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


# Configuration subcommands group
@click.group()
def config():
    """Configuration management."""
    pass


# Add to main jmp group
jmp.add_command(config)


@config.group("exporter")
def config_exporter():
    """Modify jumpstarter exporter config files."""
    pass


@config_exporter.command("create")
@click.option("--namespace", prompt=True, help="Jumpstarter namespace")
@click.option("--name", prompt=True, help="Exporter name")
@click.option("--endpoint", prompt=True, help="Server endpoint")
@click.option("--token", prompt=True, help="Auth token", hide_input=True)
@click.argument("alias", default="default")
def create_exporter_config(alias, namespace, name, endpoint, token):
    """Create an exporter config."""
    from jumpstarter.config.exporter import ExporterConfigV1Alpha1
    from jumpstarter.config.common import ObjectMeta
    
    try:
        ExporterConfigV1Alpha1.load(alias)
        click.echo(f'Error: exporter "{alias}" already exists', err=True)
        return
    except Exception:
        pass  # Config doesn't exist, which is expected

    config = ExporterConfigV1Alpha1(
        alias=alias,
        metadata=ObjectMeta(namespace=namespace, name=name),
        endpoint=endpoint,
        token=token,
    )
    path = ExporterConfigV1Alpha1.save(config)
    click.echo(f"Exporter config created: {path}")


@config_exporter.command("delete")
@click.argument("alias", default="default")
def delete_exporter_config(alias):
    """Delete an exporter config."""
    from jumpstarter.config.exporter import ExporterConfigV1Alpha1
    
    try:
        ExporterConfigV1Alpha1.load(alias)
    except Exception:
        click.echo(f'Error: exporter "{alias}" does not exist', err=True)
        return
        
    path = ExporterConfigV1Alpha1.delete(alias)
    click.echo(f"Exporter config deleted: {path}")


@config_exporter.command("list")
def list_exporter_configs():
    """List exporter configs."""
    from jumpstarter.config.exporter import ExporterConfigV1Alpha1
    
    exporters = ExporterConfigV1Alpha1.list()
    if not exporters.items:
        click.echo("No exporter configs found")
        return
        
    click.echo("ALIAS\t\tENDPOINT\t\tPATH")
    for exporter in exporters.items:
        click.echo(f"{exporter.alias}\t\t{exporter.endpoint or 'N/A'}\t\t{exporter.path}")


@config.group("client")
def config_client():
    """Modify jumpstarter client config files."""
    pass


@config_client.command("create")
@click.argument("alias")
@click.option("--namespace", prompt=True, help="Client namespace")
@click.option("--name", prompt=True, help="Client name")
@click.option("--endpoint", prompt=True, help="Server endpoint")
@click.option("--token", prompt=True, help="Auth token", hide_input=True)
def create_client_config(alias, namespace, name, endpoint, token):
    """Create a client config."""
    from jumpstarter.config.client import ClientConfigV1Alpha1
    from jumpstarter.config.common import ObjectMeta
    
    if ClientConfigV1Alpha1.exists(alias):
        click.echo(f'Error: client "{alias}" already exists', err=True)
        return

    config = ClientConfigV1Alpha1(
        alias=alias,
        metadata=ObjectMeta(namespace=namespace, name=name),
        endpoint=endpoint,
        token=token,
    )
    path = ClientConfigV1Alpha1.save(config)
    click.echo(f"Client config created: {path}")


@config_client.command("delete")
@click.argument("alias")
def delete_client_config(alias):
    """Delete a client config."""
    from jumpstarter.config.client import ClientConfigV1Alpha1
    
    try:
        ClientConfigV1Alpha1.load(alias)
    except Exception:
        click.echo(f'Error: client "{alias}" does not exist', err=True)
        return
        
    path = ClientConfigV1Alpha1.delete(alias)
    click.echo(f"Client config deleted: {path}")


@config_client.command("list")
def list_client_configs():
    """List client configs."""
    from jumpstarter.config.client import ClientConfigV1Alpha1
    
    clients = ClientConfigV1Alpha1.list()
    if not clients.items:
        click.echo("No client configs found")
        return
        
    click.echo("CURRENT\tALIAS\t\tENDPOINT\t\tPATH")
    for client in clients.items:
        current = "*" if clients.current_config == client.alias else " "
        click.echo(f"{current}\t{client.alias}\t\t{client.endpoint}\t\t{client.path}")


@config_client.command("use")
@click.argument("alias")
def use_client_config(alias):
    """Select the current client config."""
    from jumpstarter.config.client import ClientConfigV1Alpha1
    from jumpstarter.config.user import UserConfigV1Alpha1
    
    if not ClientConfigV1Alpha1.exists(alias):
        click.echo(f'Error: client "{alias}" does not exist', err=True)
        return
        
    user_config = UserConfigV1Alpha1.load_or_create()
    user_config.use_client(alias)
    click.echo(f"Switched to client config '{alias}'")


@jmp.command()
@click.option("--selector", help="Device selector")
@click.option("--filter", help="Filter expression")
def get(selector, filter):
    """Get resources from the server."""
    click.echo("🚧 Resource listing functionality coming soon")
    click.echo("This will connect to the standalone server and list:")
    click.echo("  - exporters")
    click.echo("  - devices")
    click.echo("  - leases")


@jmp.command()
@click.argument("selector")
@click.option("--duration", default="30m", help="Lease duration")
def create(selector, duration):
    """Create a lease for a device."""
    click.echo(f"🚧 Creating lease for selector: {selector}")
    click.echo(f"Duration: {duration}")
    click.echo("This will connect to the standalone server to create device leases")


@jmp.command()
@click.argument("name")
def delete(name):
    """Delete a lease."""
    click.echo(f"🚧 Deleting lease: {name}")
    click.echo("This will connect to the standalone server to delete leases")


@jmp.command()
@click.argument("selector")
@click.option("--duration", default="30m", help="Lease duration")
def shell(selector, duration):
    """Open an interactive shell to a device."""
    click.echo(f"🚧 Opening shell to device: {selector}")
    click.echo(f"Duration: {duration}")
    click.echo("This will connect to the standalone server and open an interactive session")


if __name__ == "__main__":
    jmp()
