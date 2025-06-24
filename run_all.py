import subprocess
import time
import sys
import os
import argparse

def run_server():
    """Starts the gRPC server in a separate process."""
    print("Starting gRPC server...")
    # Use sys.executable to ensure the correct Python interpreter is used
    # Add 'src' to PYTHONPATH for the server to find its modules
    server_process = subprocess.Popen(
        [sys.executable, "-m", "src.server.server"],
        env=dict(os.environ, PYTHONPATH=os.path.abspath("src"))
    )
    print(f"Server process started with PID: {server_process.pid}")
    return server_process

def run_client_cli(freq, gain, device_id):
    """Starts the gRPC CLI client in a separate process."""
    print("Starting gRPC CLI client...")
    client_cmd = [
        sys.executable,
        "-m",
        "src.client.client",
        "--freq", str(freq),
        "--gain", str(gain),
        "--id", str(device_id)
    ]
    # Add 'src' to PYTHONPATH for the client to find its modules
    client_process = subprocess.run(
        client_cmd,
        env=dict(os.environ, PYTHONPATH=os.path.abspath("src"))
    )
    print("CLI client finished.")

def run_client_ui():
    """Starts the gRPC UI client in a separate process."""
    print("Starting gRPC UI client...")
    client_cmd = [
        sys.executable,
        "-m",
        "src.client.client_ui"
    ]
    # Add 'src' to PYTHONPATH for the client to find its modules
    client_process = subprocess.run(
        client_cmd,
        env=dict(os.environ, PYTHONPATH=os.path.abspath("src"))
    )
    print("UI client finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run gRPC RF Control Server and Client")
    parser.add_argument(
        "--client-type",
        type=str,
        choices=["cli", "ui"],
        default="cli",
        help="Type of client to run (cli or ui)"
    )
    parser.add_argument(
        "--freq", type=float, default=915.0, help="RF frequency in MHz (for CLI client)"
    )
    parser.add_argument(
        "--gain", type=float, default=20.0, help="RF gain in dB (for CLI client)"
    )
    parser.add_argument(
        "--id", type=str, default="DEV001", help="Device ID to configure (for CLI client)"
    )
    args = parser.parse_args()

    server_proc = None
    try:
        server_proc = run_server()
        # Give the server some time to start up
        time.sleep(3)

        if args.client_type == "cli":
            run_client_cli(args.freq, args.gain, args.id)
        elif args.client_type == "ui":
            run_client_ui()

    except KeyboardInterrupt:
        print("\nOrchestrator interrupted. Shutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if server_proc and server_proc.poll() is None:
            print("Terminating server process...")
            server_proc.terminate()
            server_proc.wait(timeout=5)
            print("Server process terminated.")
        elif server_proc:
            print("Server process already exited.")
