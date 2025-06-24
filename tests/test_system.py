import pytest
import subprocess
import sys
import time
import os

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="module")
def server_process():
    """Fixture to start and stop the gRPC server for system tests."""
    # Start the server in a separate process
    server_cmd = [sys.executable, "-m", "src.server.server"]
    # Use a different port for testing to avoid conflicts
    # For this example, we'll stick to the default, but in a real CI
    # environment, you might pass a port argument.
    process = subprocess.Popen(
        server_cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        # The server needs to find its modules
        env=dict(os.environ, PYTHONPATH="src")
    )
    
    # Give the server a moment to start up
    time.sleep(2)
    
    # Check if the process is still running
    assert process.poll() is None, "Server failed to start."

    yield process

    # Teardown: stop the server
    process.terminate()
    process.wait(timeout=5)

def test_client_server_communication(server_process):
    """
    A system test to verify end-to-end communication between the
    client and server.
    """
    # Arrange
    client_cmd = [
        sys.executable,
        "-m",
        "src.client.client",
        "--freq", "99.9",
        "--gain", "15.5",
        "--id", "SYS_TEST_01"
    ]
    
    # Act
    result = subprocess.run(
        client_cmd,
        capture_output=True,
        text=True,
        check=True,
        # The client needs to find its modules
        env=dict(os.environ, PYTHONPATH="src")
    )

    # Assert
    # The client logs to stderr by default with basicConfig
    assert "Server Response: Success=True" in result.stderr
    assert "Status='OPERATING - Freq: 99.9MHz, Gain: 15.5dB'" in result.stderr
