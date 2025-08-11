# Jumpstarter Client Tools

This directory contains the integrated Python client tools from the [jumpstarter repository](https://github.com/jumpstarter-dev/jumpstarter), providing a unified development experience alongside the standalone server.

## Overview

The client tools include:

- **jumpstarter-cli** - Command-line interface (`jmp`, `j` commands)
- **jumpstarter** - Core Python library for device automation
- **jumpstarter-protocol** - Protocol buffers and gRPC definitions
- **jumpstarter-testing** - Testing utilities and framework integration
- **drivers/** - Hardware drivers for various devices and interfaces

## Installation

From the repository root:

```bash
cd client
pip install -e .
```

For development with all drivers:

```bash
pip install -e ".[all]"
```

## Usage

After installation, you can use the CLI tools:

```bash
# Main CLI interface
jmp --help

# Short alias
j --help
```

## Integration with Standalone Server

These client tools are designed to work seamlessly with the standalone server:

1. **Server Configuration**: The standalone server provides the gRPC endpoints
2. **Client Connection**: Use `jmp login` to connect to your standalone server
3. **Device Management**: Manage and interact with devices through the unified CLI

## Documentation

See the main [jumpstarter documentation](https://jumpstarter.dev) for detailed usage instructions.