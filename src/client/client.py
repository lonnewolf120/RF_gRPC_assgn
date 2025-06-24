import grpc
import logging
import argparse

# Import generated classes
import rfcontrol_pb2
import rfcontrol_pb2_grpc

logging.basicConfig(level=logging.INFO)

def run(frequency: float, gain: float, device_id: str, server_addr: str):
    """Contacts the gRPC server and sends RF settings."""
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel(server_addr) as channel:
        stub = rfcontrol_pb2_grpc.RFControlStub(channel)
        try:
            response = stub.SetRFSettings(
                rfcontrol_pb2.RFConfig(
                    frequency=frequency, gain=gain, device_id=device_id
                )
            )
            logging.info(f"Server Response: Success={response.success}, Status='{response.device_status}'")
        except grpc.RpcError as e:
            logging.error(f"RPC failed: {e.code()} - {e.details()}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="gRPC RF Control Client")
    parser.add_argument(
        "--server", type=str, default="localhost:50051", help="Server address"
    )
    parser.add_argument(
        "--freq", type=float, default=915.0, help="RF frequency in MHz"
    )
    parser.add_argument(
        "--gain", type=float, default=20.0, help="RF gain in dB"
    )
    parser.add_argument(
        "--id", type=str, default="DEV001", help="Device ID to configure"
    )
    args = parser.parse_args()

    run(args.freq, args.gain, args.id, args.server)
