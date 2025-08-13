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
    from jumpstarter.grpc_client import JumpstarterClient
    
    try:
        with JumpstarterClient() as client:
            if not client.test_connection():
                click.echo("✗ Could not connect to jumpstarter server")
                click.echo("Make sure the server is running:")
                click.echo("  docker-compose up -d")
                return
                
            click.echo("📋 Listing resources from server...")
            
            # List devices/exporters
            devices = client.get_devices(selector)
            if devices:
                click.echo("\nDEVICES:")
                click.echo("NAME\t\tNAMESPACE\tSTATUS\t\tLABELS")
                for device in devices:
                    labels_str = ",".join([f"{k}={v}" for k, v in device.get("labels", {}).items()])
                    click.echo(f"{device['name']}\t{device['namespace']}\t{device['status']}\t{labels_str}")
            
            # List leases 
            leases = client.list_leases()
            if leases:
                click.echo("\nLEASES:")
                for lease in leases:
                    click.echo(f"  {lease}")
            
            if not devices and not leases:
                click.echo("No resources found")
                
    except Exception as e:
        click.echo(f"✗ Error connecting to server: {e}")
        click.echo("Make sure the jumpstarter standalone server is running")


@jmp.command()
@click.argument("selector")
@click.option("--duration", default="30m", help="Lease duration")
def create(selector, duration):
    """Create a lease for a device."""
    from jumpstarter.grpc_client import JumpstarterClient
    
    try:
        with JumpstarterClient() as client:
            if not client.test_connection():
                click.echo("✗ Could not connect to jumpstarter server")
                return
                
            click.echo(f"📝 Creating lease for selector: {selector}")
            click.echo(f"Duration: {duration}")
            
            # Parse selector into dict (simple key=value format)
            selector_dict = {}
            if "=" in selector:
                for part in selector.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        selector_dict[k.strip()] = v.strip()
            
            lease_name = client.request_lease(selector_dict, duration)
            click.echo(f"✓ Lease created: {lease_name}")
            
    except Exception as e:
        click.echo(f"✗ Error creating lease: {e}")


@jmp.command()
@click.argument("name")
def delete(name):
    """Delete a lease."""
    from jumpstarter.grpc_client import JumpstarterClient
    
    try:
        with JumpstarterClient() as client:
            if not client.test_connection():
                click.echo("✗ Could not connect to jumpstarter server")
                return
                
            click.echo(f"🗑️  Deleting lease: {name}")
            
            success = client.release_lease(name)
            if success:
                click.echo(f"✓ Lease {name} deleted successfully")
            else:
                click.echo(f"✗ Failed to delete lease {name}")
                
    except Exception as e:
        click.echo(f"✗ Error deleting lease: {e}")


@jmp.command()
@click.argument("selector")
@click.option("--duration", default="30m", help="Lease duration")
def shell(selector, duration):
    """Open an interactive shell to a device."""
    from jumpstarter.grpc_client import JumpstarterClient
    
    try:
        with JumpstarterClient() as client:
            if not client.test_connection():
                click.echo("✗ Could not connect to jumpstarter server")
                return
                
            click.echo(f"🖥️  Opening shell to device: {selector}")
            click.echo(f"Duration: {duration}")
            
            # For now, show the planned functionality
            click.echo("Shell functionality framework ready!")
            click.echo("This will:")
            click.echo("  1. Create a lease for the device")
            click.echo("  2. Connect to the router service")
            click.echo("  3. Open an interactive terminal session")
            click.echo("  4. Handle device communication protocols")
            click.echo("")
            click.echo("📋 Implementation status:")
            click.echo("  ✓ gRPC client framework") 
            click.echo("  ✓ Server connectivity")
            click.echo("  🚧 Interactive shell protocol (next step)")
                
    except Exception as e:
        click.echo(f"✗ Error connecting to device: {e}")


if __name__ == "__main__":
    jmp()
