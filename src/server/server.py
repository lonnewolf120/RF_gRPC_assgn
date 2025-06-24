import grpc
import time
import logging
from concurrent import futures

# Import generated classes
import rfcontrol_pb2
import rfcontrol_pb2_grpc

from server.rf_device import SimulatedRFDevice

logging.basicConfig(level=logging.INFO)

class RFControlServicer(rfcontrol_pb2_grpc.RFControlServicer):
    """Provides methods that implement functionality of RF control server."""

    def __init__(self):
        self.device = SimulatedRFDevice()
        # Automatically connect to a default device on startup
        self.device.connect("DEV001")

    def SetRFSettings(self, request, context):
        """Handles the SetRFSettings RPC."""
        logging.info(
            f"Received SetRFSettings request: Freq={request.frequency}MHz, "
            f"Gain={request.gain}dB, DeviceID='{request.device_id}'"
        )

        # Use the simulated device
        success_freq = self.device.set_frequency(request.frequency)
        success_gain = self.device.set_gain(request.gain)

        # Determine overall success
        success = success_freq and success_gain
        
        # Get the latest status from the device
        status = self.device.status

        if not success:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to apply RF settings on the device.")

        return rfcontrol_pb2.RFResponse(success=success, device_status=status)

def serve():
    """Starts the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rfcontrol_pb2_grpc.add_RFControlServicer_to_server(RFControlServicer(), server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    logging.info("Server started on port 50051.")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        logging.info("Server stopping...")
        server.stop(0)
        logging.info("Server stopped.")

if __name__ == '__main__':
    serve()
