"""Short alias 'j' for the jmp command."""

import click


def j():
    """Short alias for the Jumpstarter CLI."""
    click.echo("Jumpstarter client tools (j alias)")
    click.echo("Full integration coming soon. Use 'jmp' for current functionality.")


if __name__ == "__main__":
    j()