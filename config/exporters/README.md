# Jumpstarter Mock Exporters

This directory contains example configurations and mock implementations for Jumpstarter exporters that work with the standalone server.

## Files

- **`mock-demo.yaml`** - Comprehensive mock exporter configuration with multiple device types
- **`simple-mock.yaml`** - Minimal mock exporter configuration for basic testing
- **`mock_exporter.py`** - Python implementation of a mock exporter for testing

## Quick Start

### 1. Start the Standalone Server

Make sure your jumpstarter standalone server is running:

```bash
# From the repository root
docker-compose up -d
```

The server should be accessible at `localhost:8080`.

### 2. Run the Mock Exporter

```bash
# From the repository root
cd config/exporters
python3 mock_exporter.py mock-demo.yaml
```

Or using uv from the client directory:

```bash
# From the client directory
cd ../../client
uv run python ../config/exporters/mock_exporter.py ../config/exporters/mock-demo.yaml
```

**Using the convenient start script:**

```bash
# Basic usage
./config/exporters/start-mock-exporter.sh

# With specific configuration
./config/exporters/start-mock-exporter.sh config/exporters/simple-mock.yaml

# With labels and additional options
./config/exporters/start-mock-exporter.sh config/exporters/mock-demo.yaml \
  --label env=development \
  --label location=lab1 \
  --debug \
  --timeout 5 \
  --no-demo
```

**Available arguments:**

- `--label key=value` - Add labels (can be used multiple times)
- `--debug` - Enable debug logging
- `--timeout N` - Status update interval in seconds (default: 10)
- `--no-demo` - Skip the initial demo sequence

### 3. Monitor the Exporter

The mock exporter will:

- Connect to the standalone server at `localhost:8080`
- Simulate hardware devices (power, serial, storage)
- Run a demonstration of capabilities
- Provide periodic status updates

Press `Ctrl+C` to stop the exporter.

## Configuration Format

The YAML configuration follows the standard Jumpstarter ExporterConfig format:

```yaml
apiVersion: jumpstarter.dev/v1alpha1
kind: ExporterConfig
metadata:
  namespace: default
  name: mock-demo
endpoint: localhost:8080
grpcConfig:
  grpc.keepalive_time_ms: 20000
export:
  power:
    type: jumpstarter_driver_mock.driver.MockPower
    config:
      name: "Mock Power Switch"
      initial_state: "off"
  # ... more devices
```

## Mock Devices

The mock exporter simulates these device types:

### Power Control

- **Type**: `MockPower`
- **Capabilities**: On/Off control, status reporting
- **Use case**: Simulates relay or power switch

### Serial Console

- **Type**: `MockSerial`
- **Capabilities**: Command/response simulation, startup banner
- **Use case**: Simulates UART or console access

### Storage Device

- **Type**: `MockStorage`
- **Capabilities**: Mount/unmount, capacity reporting
- **Use case**: Simulates SD card or USB storage

### GPIO Control

- **Type**: `MockGPIO`
- **Capabilities**: Pin control, state management
- **Use case**: Simulates GPIO expander or digital I/O

## Integration with Client Tools

Once the mock exporter is running, you can test client interactions:

```bash
# Login to the server
cd client
uv run jmp login --server localhost:8080

# List available devices (when implemented)
uv run jmp get devices

# Get device status (when implemented)
uv run jmp get status
```

## Development Notes

This mock implementation is for testing and development purposes. It simulates the behavior of real hardware drivers without requiring actual hardware connections.

In a production environment, you would:

1. Install real jumpstarter drivers (e.g., `jumpstarter-driver-yepkit`, `jumpstarter-driver-pyserial`)
2. Configure the exporter with actual device paths and settings
3. Run the exporter on hardware that has physical connections to your devices

## Troubleshooting

### Connection Issues

- Verify the standalone server is running: `curl http://localhost:8080`
- Check that no firewall is blocking port 8080
- Ensure the endpoint in the config matches your server address

### Python Issues

- Make sure Python 3.11+ is installed
- Install required dependencies if using real drivers
- Check Python path if running outside the uv environment
