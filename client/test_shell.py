#!/usr/bin/env python3
"""
Simple test shell to demonstrate mock device interaction
"""

import random  # nosec B311
import time


def handle_command(cmd: str) -> bool:
    """Handle individual shell commands. Returns True to continue, False to exit."""
    if cmd.lower() in ["exit", "quit"]:
        print("Disconnecting from device...")
        print("Lease released.")
        return False
    elif cmd.lower() == "help":
        print("Available commands:")
        print("  help     - Show this help")
        print("  status   - Show device status")
        print("  power    - Toggle power")
        print("  reboot   - Reboot device")
        print("  uptime   - Show uptime")
        print("  exit     - Exit shell")
    elif cmd.lower() == "status":
        print("Device Status: Online")
        print(f"Power: {'ON' if random.choice([True, False]) else 'OFF'}")  # nosec B311
        print(f"Temperature: {random.randint(35, 65)}°C")  # nosec B311
        print(f"Memory: {random.randint(20, 80)}% used")  # nosec B311
    elif cmd.lower() == "power":
        state = "ON" if random.choice([True, False]) else "OFF"  # nosec B311
        print(f"Power toggled: {state}")
    elif cmd.lower() == "reboot":
        print("Rebooting device...")
        time.sleep(1)
        print("Device rebooted successfully")
    elif cmd.lower() == "uptime":
        hours = random.randint(1, 72)  # nosec B311
        mins = random.randint(0, 59)  # nosec B311
        print(f"Uptime: {hours}h {mins}m")
    elif cmd == "":
        pass  # Empty command, continue
    else:
        print(f"Unknown command: {cmd}")
        print("Type 'help' for available commands")
    return True


def mock_shell_session():
    print("🖥️  Jumpstarter Shell - Mock Device Session")
    print("=" * 50)
    print("Connected to: mock-device-1 (type=device,model=pi4)")
    print("Lease: lease-12345 (Duration: 30m)")
    print("=" * 50)
    print()
    print("Mock Device Console v1.0")
    print("Type 'help' for available commands, 'exit' to quit")
    print()

    while True:
        try:
            cmd = input("mock-device> ").strip()
            if not handle_command(cmd):
                break
        except KeyboardInterrupt:
            print("\nExiting shell...")
            break
        except EOFError:
            print("\nExiting shell...")
            break


if __name__ == "__main__":
    mock_shell_session()
