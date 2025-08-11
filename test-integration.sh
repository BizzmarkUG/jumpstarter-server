#!/bin/bash
# Integration test script for jumpstarter-server monorepo

set -e

echo "=== Jumpstarter Server + Client Integration Test ==="
echo

# Check if we're in the right directory
if [ ! -f "cmd/standalone/main.go" ]; then
    echo "Error: Please run this script from the repository root"
    exit 1
fi

echo "1. Building standalone server..."
go build -o bin/standalone cmd/standalone/main.go
echo "✓ Standalone server built successfully"
echo

echo "2. Installing client CLI tools..."
cd client/packages/jumpstarter-cli
pip install -e . --quiet
cd ../../..
echo "✓ Client CLI tools installed"
echo

echo "3. Testing CLI tools..."
echo "CLI version:"
jmp version
echo

echo "4. Testing server connectivity (without server running)..."
jmp login --server localhost:8080 || true
echo

echo "5. Starting standalone server in background..."
mkdir -p /tmp/jumpstarter
./bin/standalone --config /tmp/jumpstarter/config.yaml &
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for server to start
sleep 3

echo "6. Testing client connection to running server..."
jmp login --server localhost:8080
echo

echo "7. Cleaning up..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true
echo "✓ Server stopped"
echo

echo "=== Integration Test Completed Successfully ==="
echo "The jumpstarter monorepo is working correctly!"
echo
echo "Next steps:"
echo "- Use 'docker-compose up -d' for easy server deployment"
echo "- Use 'jmp --help' to explore CLI commands"
echo "- See client/INTEGRATION.md for development guide"
