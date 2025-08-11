# Jumpstarter Standalone Mode

This directory contains configuration and deployment files for running Jumpstarter in standalone mode, without requiring Kubernetes infrastructure.

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/BizzmarkUG/jumpstarter-server.git
   cd jumpstarter-server
   ```

2. **Start the services**:

   ```bash
   docker-compose up -d
   ```

3. **Check the logs**:

   ```bash
   docker-compose logs -f jumpstarter
   ```

4. **Access the services**:
   - Controller API: http://localhost:8080
   - Router Service: http://localhost:8090
   - Dashboard (if enabled): http://localhost:8086

### Using Docker directly

1. **Build the standalone image**:

   ```bash
   docker build -f Dockerfile.standalone -t jumpstarter:standalone .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name jumpstarter \
     -p 8080:8080 \
     -p 8090:8090 \
     -v $(pwd)/config:/etc/jumpstarter:ro \
     -e CONTROLLER_KEY=your-secret-key \
     jumpstarter:standalone
   ```

### Manual build and run

1. **Build the standalone binary**:

   ```bash
   go build -o bin/standalone cmd/standalone/main.go
   ```

2. **Run with custom configuration**:
   ```bash
   ./bin/standalone \
     --config=./config/config.yaml \
     --controller-addr=:8080 \
     --router-addr=:8090
   ```

## Configuration

### Configuration File

The standalone mode uses a YAML configuration file (default: `/etc/jumpstarter/config.yaml`).

Example configuration:

```yaml
authentication:
  internal:
    prefix: "jumpstarter"

router:
  default:
    endpoint: "localhost:8090"
    labels: {}

grpc:
  keepalive:
    minTime: "1s"
    permitWithoutStream: true
```

### Environment Variables

- `CONTROLLER_KEY`: Secret key for internal OIDC signing (required)

### Command Line Options

- `--config`: Path to configuration file (default: `/etc/jumpstarter/config.yaml`)
- `--controller-addr`: Address for controller service (default: `:8080`)
- `--router-addr`: Address for router service (default: `:8090`)
- `--enable-http2`: Enable HTTP/2 (default: false)

## Differences from Kubernetes Mode

### What's Included

- Combined controller and router services in a single process
- File-based configuration instead of ConfigMaps
- In-memory storage for device/exporter state
- Simplified authentication and authorization
- Self-contained deployment without external dependencies

### What's Not Included

- Kubernetes CRDs (Custom Resource Definitions)
- Kubernetes RBAC integration
- Persistent storage (state is lost on restart)
- Advanced authentication providers
- High availability / clustering

### Limitations

- No persistence - all state is lost when the container restarts
- Single instance only (no clustering)
- Simplified authentication model
- No advanced Kubernetes features

## Use Cases

This standalone mode is ideal for:

- **Development and testing environments**
- **Small deployments** with just a few devices
- **Edge computing** scenarios
- **Organizations without Kubernetes expertise**
- **Quick prototyping and demos**

## Security Considerations

For production use, ensure you:

1. Set a strong `CONTROLLER_KEY` environment variable
2. Use HTTPS/TLS for external access
3. Restrict network access to the service ports
4. Regularly update the container image
5. Consider using external authentication if needed

## Migration from Kubernetes

To migrate from Kubernetes-based deployment to standalone mode:

1. Export your current configuration from ConfigMaps
2. Convert the configuration to the standalone YAML format
3. Deploy using the standalone mode
4. Reconfigure your clients to use the new endpoints

Note: Device and exporter state will need to be re-registered as the standalone mode doesn't persist data.
