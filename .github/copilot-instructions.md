# Copilot Instructions for Jumpstarter Server

## Overview

This repository contains the Jumpstarter Server, a fork of jumpstarter-controller that provides a standalone mode operation without Kubernetes dependencies and serves as a monorepo integrating jumpstarter client tools from the [jumpstarter repository](https://github.com/jumpstarter-dev/jumpstarter.git).

## Project Goals

The primary goal is to transform this repository into a monorepo that:
- **Focuses on standalone mode operation** as the main deployment method
- **Integrates jumpstarter client tools** from the jumpstarter repository
- **Eliminates Kubernetes dependencies** for simpler deployment and maintenance
- **Provides a unified development experience** for both server and client components

## Step-by-Step Approach

1. ✅ Add copilot-instructions to this repo
2. Restore and enhance standalone mode functionality
3. Integrate client tools from jumpstarter repository
4. Describe what the final monorepo will look like
5. Specify tests to execute
6. Test with real jumpstarter setup

## Code Structure

- `api/` - API definitions and types
- `cmd/` - Main applications and command-line tools
  - `cmd/standalone/` - **Standalone server implementation (primary focus)**
- `internal/` - Internal packages not exposed externally
  - `internal/standalone/` - **Standalone mode server components**
- `config/` - Configuration files and samples for standalone mode
- `deploy/` - Deployment configurations (Docker, docker-compose)
- `test/` - Test files and test utilities
- `docs/` - Documentation including standalone mode setup
- `client/` - **(Planned)** Integrated client tools from jumpstarter repository

## Technology Stack

- **Language**: Go
- **Build System**: Makefile, Go modules
- **Container**: Docker (standalone mode focus)
- **Deployment**: Docker, docker-compose (primary), Helm charts (legacy)
- **APIs**: gRPC with Protocol Buffers

## Development Guidelines

- Follow Go best practices and idioms
- Maintain backwards compatibility where possible
- Add comprehensive tests for new functionality
- Update documentation for any changes
- Use semantic versioning for releases

## Dependencies

- **Eliminate Kubernetes dependencies** in standalone mode
- Prefer standard library and well-established third-party packages
- Keep dependencies up to date and secure
- Minimize external dependencies for simpler deployment

## Testing

- Unit tests for all core functionality
- Integration tests for API endpoints
- End-to-end tests with real jumpstarter setup
- Performance tests for critical paths

## Build and Development

Use the provided Makefile for common development tasks:
- `make build` - Build the application (including standalone mode)
- `make test` - Run tests
- `make lint` - Run linters
- `make clean` - Clean build artifacts

For standalone mode development:
- `docker-compose up -d` - Run standalone server with dependencies
- `go run cmd/standalone/main.go` - Run standalone server locally

## Monorepo Structure (Planned)

The repository will be restructured to include:
- **Standalone server components (primary focus)**
  - Kubernetes-free operation
  - Docker-based deployment
  - Simplified configuration and setup
- **Integrated client tools from jumpstarter repository**
  - Command-line utilities
  - Python client libraries
  - Testing and automation tools
- **Shared libraries and common code**
  - Protocol buffers and API definitions
  - Common utilities and helpers
- **Documentation and examples**
  - Standalone mode setup guides
  - Client integration examples
- **Testing infrastructure**
  - Unit, integration, and end-to-end tests
  - CI/CD pipelines for both server and client components

## Key Considerations

- Maintain API compatibility during the transition
- Ensure minimal disruption to existing users
- Provide clear migration paths
- Document all changes thoroughly
