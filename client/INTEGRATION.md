# Client Integration Guide

This directory contains the integrated Jumpstarter client tools that work with the standalone server.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Standalone jumpstarter server running

### Basic Installation

1. **Install the CLI tools**:

   ```bash
   cd client/packages/jumpstarter-cli
   pip install -e .
   ```

2. **Test the installation**:
   ```bash
   jmp --help
   jmp version
   ```

### Connecting to the Standalone Server

1. **Start the standalone server**:

   ```bash
   # From the repository root
   docker-compose up -d
   # or
   go run cmd/standalone/main.go
   ```

2. **Connect with the CLI**:
   ```bash
   jmp login --server localhost:8080
   ```

## Development Status

### ✅ Completed

- Basic CLI structure (`jmp`, `j` commands)
- Package structure for monorepo integration
- Basic client library skeleton
- Documentation framework

### 🚧 In Progress

- Full CLI command implementation
- gRPC client integration with standalone server
- Protocol buffer definitions
- Advanced device management

### 📋 Planned

- All driver packages integration
- Complete testing framework
- Examples and tutorials
- Advanced features (device drivers, automation scripts)

## Architecture

The client tools are organized as a Python workspace:

```
client/
├── packages/
│   ├── jumpstarter-cli/     # Main CLI interface
│   ├── jumpstarter/         # Core Python library
│   └── (more packages...)   # Additional tools and drivers
├── pyproject.toml           # Workspace configuration
└── README.md               # This file
```

## Integration Notes

This integration provides:

1. **Unified Development**: Client and server tools in one repository
2. **Standalone Focus**: Optimized for standalone deployment (no Kubernetes)
3. **Simplified Setup**: Single repository clone and setup
4. **Consistent Tooling**: Shared development practices and documentation
