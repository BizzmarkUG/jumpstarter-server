#!/bin/bash
#
# Start Mock Exporter for Jumpstarter Standalone Server
#
# This script starts a mock exporter that simulates hardware devices
# and connects to the jumpstarter standalone server at localhost:8080
#

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Configuration file (default to mock-demo.yaml)
# First argument is config file, rest are passed to the exporter
CONFIG_FILE="${1:-$SCRIPT_DIR/mock-demo.yaml}"

# Shift to remove config file from arguments, keeping the rest for the exporter
if [[ $# -gt 0 ]]; then
    shift
fi
EXPORTER_ARGS="$*"

echo "=== Jumpstarter Mock Exporter ==="
echo "Repository root: $REPO_ROOT"
echo "Configuration: $CONFIG_FILE"
echo "Server endpoint: localhost:8080"
if [[ -n "$EXPORTER_ARGS" ]]; then
    echo "Additional arguments: $EXPORTER_ARGS"
fi
echo ""

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Configuration file not found: $CONFIG_FILE"
    echo ""
    echo "Available configurations:"
    find "$SCRIPT_DIR" -name "*.yaml" -type f
    echo ""
    echo "Usage: $0 [config-file] [additional-args...]"
    echo "Example: $0 $SCRIPT_DIR/simple-mock.yaml --label env=dev --label location=lab1"
    echo "Example: $0 $SCRIPT_DIR/mock-demo.yaml --debug --timeout 30"
    exit 1
fi

# Check if standalone server is running
echo "Checking if standalone server is running..."
if ! curl -s http://localhost:8080 >/dev/null 2>&1; then
    echo "Warning: Cannot connect to standalone server at localhost:8080"
    echo "Make sure to start the server first:"
    echo "  cd $REPO_ROOT && docker-compose up -d"
    echo ""
    echo "Continuing anyway (for testing purposes)..."
else
    echo "✓ Standalone server is running at localhost:8080"
fi

echo ""
echo "Starting mock exporter..."
echo "Press Ctrl+C to stop"
echo ""

# Start the mock exporter
cd "$REPO_ROOT"
exec python3 "$SCRIPT_DIR/mock_exporter.py" "$CONFIG_FILE" $EXPORTER_ARGS
