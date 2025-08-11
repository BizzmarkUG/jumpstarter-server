#!/usr/bin/env python3
"""
Simple Mock Exporter for Jumpstarter Standalone Server

This is a basic mock exporter that simulates hardware interfaces
and can be used for testing the jumpstarter standalone server.
"""

import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockPowerDriver:
    """Mock power control driver."""

    def __init__(self, name: str = "Mock Power", initial_state: str = "off"):
        self.name = name
        self.state = initial_state
        logger.info(f"Initialized {self.name} with state: {self.state}")

    def power_on(self):
        """Turn power on."""
        self.state = "on"
        logger.info(f"{self.name}: Power ON")
        return {"status": "on", "timestamp": time.time()}

    def power_off(self):
        """Turn power off."""
        self.state = "off"
        logger.info(f"{self.name}: Power OFF")
        return {"status": "off", "timestamp": time.time()}

    def get_status(self):
        """Get current power status."""
        return {"status": self.state, "device": self.name}


class MockSerialDriver:
    """Mock serial console driver."""

    def __init__(
        self,
        name: str = "Mock Serial",
        baudrate: int = 115200,
        startup_banner: str = "Mock Device Console v1.0\n",
    ):
        self.name = name
        self.baudrate = baudrate
        self.startup_banner = startup_banner
        self.connected = False
        logger.info(f"Initialized {self.name} at {self.baudrate} baud")

    def connect(self):
        """Connect to serial console."""
        self.connected = True
        logger.info(f"{self.name}: Connected")
        return self.startup_banner

    def disconnect(self):
        """Disconnect from serial console."""
        self.connected = False
        logger.info(f"{self.name}: Disconnected")

    def send_command(self, command: str):
        """Send command and get mock response."""
        if not self.connected:
            return "ERROR: Not connected"

        # Mock responses for common commands
        responses = {
            "help": "Available commands: help, status, reboot, echo",
            "status": "System Status: OK, Uptime: 42 minutes",
            "reboot": "Rebooting system...",
            "": "",
        }

        response = responses.get(command.strip(), f"Unknown command: {command}")
        logger.info(f"{self.name}: Command '{command}' -> '{response}'")
        return response


class MockStorageDriver:
    """Mock storage device driver."""

    def __init__(self, name: str = "Mock Storage", size_mb: int = 1024):
        self.name = name
        self.size_mb = size_mb
        self.mounted = False
        logger.info(f"Initialized {self.name} with {self.size_mb}MB capacity")

    def mount(self):
        """Mount storage device."""
        self.mounted = True
        logger.info(f"{self.name}: Mounted")
        return {"status": "mounted", "size_mb": self.size_mb}

    def unmount(self):
        """Unmount storage device."""
        self.mounted = False
        logger.info(f"{self.name}: Unmounted")
        return {"status": "unmounted"}

    def get_info(self):
        """Get storage device information."""
        return {
            "name": self.name,
            "size_mb": self.size_mb,
            "mounted": self.mounted,
            "free_space_mb": random.randint(100, self.size_mb - 100),  # nosec B311 - mock data only
        }


class MockExporter:
    """Main mock exporter that simulates hardware access."""

    def __init__(self, config_file: str, labels=None):
        self.config_file = config_file
        self.server_endpoint = "localhost:8080"
        self.devices = {}
        self.running = False
        self.labels = labels or {}

        # Initialize mock devices
        self.devices["power"] = MockPowerDriver("Mock Power Switch")
        self.devices["serial"] = MockSerialDriver("Mock Serial Console")
        self.devices["storage"] = MockStorageDriver("Mock Storage Device")

        logger.info(f"Mock Exporter initialized with config: {config_file}")
        logger.info(f"Server endpoint: {self.server_endpoint}")
        if self.labels:
            logger.info(f"Labels: {self.labels}")

    def start(self):
        """Start the mock exporter."""
        logger.info("Starting Mock Exporter...")
        self.running = True

        # Simulate startup sequence
        logger.info("Connecting to devices...")
        self.devices["serial"].connect()

        logger.info("Registering with server...")
        # In a real implementation, this would connect via gRPC to the server

        logger.info("Mock Exporter started successfully!")
        return True

    def stop(self):
        """Stop the mock exporter."""
        logger.info("Stopping Mock Exporter...")
        self.running = False

        # Cleanup
        self.devices["serial"].disconnect()
        if self.devices["storage"].mounted:
            self.devices["storage"].unmount()

        logger.info("Mock Exporter stopped.")

    def get_device_status(self):
        """Get status of all mock devices."""
        status = {}
        for name, device in self.devices.items():
            if hasattr(device, "get_status"):
                status[name] = device.get_status()
            elif hasattr(device, "get_info"):
                status[name] = device.get_info()
            else:
                status[name] = {"name": getattr(device, "name", name)}
        return status

    def run_demo(self):
        """Run a demonstration of the mock exporter capabilities."""
        logger.info("=== Mock Exporter Demo ===")

        # Power control demo
        logger.info("Demonstrating power control...")
        self.devices["power"].power_on()
        time.sleep(1)
        self.devices["power"].power_off()

        # Serial console demo
        logger.info("Demonstrating serial console...")
        commands = ["help", "status", "echo test"]
        for cmd in commands:
            self.devices["serial"].send_command(cmd)
            time.sleep(0.5)

        # Storage demo
        logger.info("Demonstrating storage...")
        self.devices["storage"].mount()
        info = self.devices["storage"].get_info()
        logger.info(f"Storage info: {info}")
        self.devices["storage"].unmount()

        logger.info("=== Demo Complete ===")


def main():
    """Main entry point for mock exporter."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Mock Exporter for Jumpstarter Standalone Server"
    )
    parser.add_argument(
        "config_file",
        nargs="?",
        default="config/exporters/mock-demo.yaml",
        help="Path to exporter configuration file",
    )
    parser.add_argument(
        "--label",
        action="append",
        dest="labels",
        help="Add labels in key=value format (can be used multiple times)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Status update interval in seconds (default: 10)",
    )
    parser.add_argument(
        "--no-demo", action="store_true", help="Skip the initial demo sequence"
    )

    args = parser.parse_args()

    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # Parse labels
    labels = {}
    if args.labels:
        for label in args.labels:
            if "=" in label:
                key, value = label.split("=", 1)
                labels[key] = value
                logger.info(f"Added label: {key}={value}")
            else:
                logger.warning(f"Invalid label format (expected key=value): {label}")

    config_file = args.config_file
    exporter = MockExporter(config_file, labels=labels)

    try:
        exporter.start()

        # Run demo unless disabled
        if not args.no_demo:
            exporter.run_demo()

        # Keep running and simulate periodic status updates
        logger.info(
            f"Mock Exporter running... (Status updates every {args.timeout}s, Ctrl+C to stop)"
        )
        while exporter.running:
            time.sleep(args.timeout)
            status = exporter.get_device_status()
            if labels:
                status["labels"] = labels
            logger.info(f"Device status: {status}")

    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        exporter.stop()


if __name__ == "__main__":
    main()
