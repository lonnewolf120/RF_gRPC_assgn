# gRPC RF Device Control System

This project implements a client-server system to control a simulated RF device using gRPC, demonstrating essential RF configuration capabilities. It includes a gRPC service definition, server and client implementations, a mocked RF API, unit/system tests, and Dockerization for easy deployment.

Logs:
![Log_and_UI.png](https://github.com/lonnewolf120/RF_gRPC_assgn/blob/master/Log_and_UI.png?raw=true)

## Table of Contents

- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Running the System](#running-the-system)
  - [Running Natively (Python)](#running-natively-python)
  - [Running with Docker Compose](#running-with-docker-compose)
- [Testing](#testing)
  - [Unit Tests](#unit-tests)
  - [System/Integration Tests](#systemintegration-tests)
- [RF API Simulation (VISA/UHD Mocking)](#rf-api-simulation-visauhd-mocking)
- [Deliverables](#deliverables)

## System Architecture

The system follows a client-server model, with communication facilitated by gRPC.
![system_architecture](https://github.com/lonnewolf120/RF_gRPC_assgn/blob/master/system_architecture.png?raw=true)

**Explanation of Components:**
*   **Client CLI:** A command-line interface for users to input RF settings.
*   **gRPC Stub:** Auto-generated code on the client side that provides local methods for calling the remote server.
*   **gRPC Server:** Listens for network requests and routes them to the appropriate service implementation.
*   **RF Control Service:** The core server-side logic that implements the `SetRFSettings` RPC, processes requests, and interacts with the hardware API.
*   **Simulated RF API:** A mock component that simulates a real RF device. This allows for development and testing without physical hardware.
*   **Docker Containers:** The client and server are packaged into separate containers to ensure consistent environments and easy deployment.

## Project Structure

```
.
├── Dockerfile.client
├── Dockerfile.server
├── README.md
├── requirements.txt
├── docker-compose.yml
├── src/
│   ├── client/
│   │   ├── __init__.py
│   │   ├── client.py       # CLI client
│   │   └── client_ui.py    # UI client (new)
│   ├── proto/
│   │   └── rfcontrol.proto
│   ├── server/
│   │   ├── __init__.py
│   │   ├── rf_device.py
│   │   └── server.py
│   ├── rfcontrol_pb2.py         (Generated by protoc)
│   └── rfcontrol_pb2_grpc.py    (Generated by protoc)
└── tests/
    ├── __init__.py
    ├── test_server.py
    └── test_system.py
```

## Prerequisites

- Python 3.9+
- pip (Python package installer)
- Docker and Docker Compose (for containerized deployment)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Generate gRPC Python code:**
    This step compiles the `.proto` definition into Python classes that the client and server use.
    ```bash
    python -m grpc_tools.protoc -I./src/proto --python_out=./src --grpc_python_out=./src ./src/proto/rfcontrol.proto
    ```
    *Note: This command is also run inside the Dockerfiles during image build.*

## Running the System

### Running Natively (Python)

1.  **Run Server and Client (Single Command):**
    You can run both the server and a client (CLI or UI) with a single command.

    **For CLI Client:**
    ```bash
    # Ensure your virtual environment is activated
    python run_all.py --client-type cli --freq 915.0 --gain 20.0 --id DEV001
    ```
    You can modify the `--freq`, `--gain`, and `--id` parameters as needed. The server will start in the background, and the CLI client will execute its request.

    **For UI Client (Optional Enhancement):**
    ```bash
    # Ensure your virtual environment is activated
    python run_all.py --client-type ui
    ```
    This will start the server in the background and then launch the Tkinter UI.

    *Note: The UI client is designed to run natively and is not included in the Docker Compose setup due to the complexities of running graphical applications within Docker containers.*

2.  **Run Components Separately (Advanced/Debugging):**

    **Start the gRPC Server:**
    Open a new terminal and run:
    ```bash
    # Ensure your virtual environment is activated
    python -m src.server.server
    ```
    The server will start and listen on `localhost:50051`. You should see log messages indicating device connection and status.

    **Run the gRPC CLI Client:**
    Open another terminal and run:
    ```bash
    # Ensure your virtual environment is activated
    python -m src.client.client --freq 915.0 --gain 20.0 --id DEV001
    ```
    You can modify the `--freq`, `--gain`, and `--id` parameters as needed. The client will send the request to the server and display the response.

    Example:
    ```bash
    python -m src.client.client --freq 868.5 --gain 18.0 --id MY_RF_DEVICE
    ```

    **Run the gRPC UI Client (Optional Enhancement):**
    Open another terminal and run:
    ```bash
    # Ensure your virtual environment is activated
    python -m src.client.client_ui
    ```
    This will launch a simple Tkinter GUI. You can enter the RF parameters and click "Set RF Settings" to send the gRPC request. The server response will be displayed in the UI.

### Running with Docker Compose

Ensure Docker and Docker Compose are installed and running on your system.

1.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```
    This command will:
    - Build the `Dockerfile.server` and `Dockerfile.client` images.
    - Start the `server` container, exposing port 50051.
    - Start the `client` container, which will automatically connect to the `server` container and send a predefined RF configuration request.

    You will see logs from both the server (simulating RF device operations) and the client (displaying the server's response). The client container will exit after sending its request.

## Testing

The project includes both unit tests and a system/integration test.

1.  **Run all tests:**
    ```bash
    # Ensure your virtual environment is activated
    pytest
    ```

### Unit Tests

Located in `tests/test_server.py`, these tests verify the logic of the `RFControlServicer` in isolation. The `SimulatedRFDevice` is mocked to ensure that only the servicer's behavior is tested.

### System/Integration Tests

Located in `tests/test_system.py`, this test validates the end-to-end communication between the client and server. It starts the server as a subprocess, runs the client as another subprocess, and asserts that the client receives the expected response from the server.

## RF API Simulation (VISA/UHD Mocking)

Since physical RF hardware is not available, the project includes a `SimulatedRFDevice` class (`src/server/rf_device.py`). This class mimics the behavior of a real RF device API (like PyVISA or UHD) by:

-   Maintaining an internal state for frequency, gain, and device status.
-   Providing methods (`connect`, `set_frequency`, `set_gain`, `get_idn`) that simulate hardware interactions.
-   Logging all operations to the console, providing clear feedback on what actions would be performed on a real device.

This mocking strategy allows for full development and testing of the gRPC communication and RF control logic without requiring actual hardware.

### Interactive Feature: Device Status Query

An interactive feature has been added to the system, allowing the client to query the current status of the simulated RF device.

-   **New RPC:** A `GetDeviceStatus` RPC has been added to the `rfcontrol.proto` service definition.
-   **Server Implementation:** The `RFControlServicer` on the server side now handles `GetDeviceStatus` requests, returning the current status from the `SimulatedRFDevice`.
-   **UI Client Integration:** The `client_ui.py` application now includes a "Get Device Status" button. Clicking this button sends a `GetDeviceStatus` request to the server and displays the returned status in the UI. This allows for real-time monitoring of the simulated device's state.

## Deliverables

The project structure and content align with the assignment requirements:

-   `src/proto/rfcontrol.proto`: Defines the gRPC service and messages.
-   `src/server/server.py`: Implements the gRPC server and integrates with the `SimulatedRFDevice`.
-   `src/client/client.py`: Provides a CLI client to set RF parameters and display server responses.
-   `src/client/client_ui.py`: Provides a UI client for setting RF parameters (optional enhancement).
-   `README.md`: This document, providing clear instructions, explanations, and architecture details.
-   `Dockerfile.server` & `Dockerfile.client`: Dockerfiles for containerizing the server and client.
-   `docker-compose.yml`: Orchestrates the Docker containers for easy setup and execution.
-   `tests/`: Contains unit and system/integration tests.
