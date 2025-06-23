import logging

logging.basicConfig(level=logging.INFO)

class SimulatedRFDevice:
    """A simulated RF device for testing without hardware."""

    def __init__(self):
        self._is_connected = False
        self._device_id = None
        self._frequency = 0.0
        self._gain = 0.0
        self._status = "DISCONNECTED"

    def connect(self, device_id: str) -> bool:
        """Simulates connecting to the device."""
        if self._is_connected:
            logging.warning(f"Device already connected to {self._device_id}.")
            return True
        
        logging.info(f"Connecting to device '{device_id}'...")
        self._device_id = device_id
        self._is_connected = True
        self._status = "CONNECTED - IDLE"
        logging.info(f"Successfully connected to {self._device_id}.")
        return True

    def disconnect(self):
        """Simulates disconnecting from the device."""
        if not self._is_connected:
            logging.warning("No device connected.")
            return
        
        logging.info(f"Disconnecting from {self._device_id}...")
        self._is_connected = False
        self._device_id = None
        self._status = "DISCONNECTED"
        logging.info("Device disconnected.")

    def set_frequency(self, freq: float) -> bool:
        """Simulates setting the RF frequency."""
        if not self._is_connected:
            logging.error("Cannot set frequency: No device connected.")
            return False
        
        logging.info(f"Setting frequency to {freq} MHz.")
        self._frequency = freq
        self._status = f"OPERATING - Freq: {self._frequency}MHz, Gain: {self._gain}dB"
        return True

    def set_gain(self, gain: float) -> bool:
        """Simulates setting the RF gain."""
        if not self._is_connected:
            logging.error("Cannot set gain: No device connected.")
            return False
        
        logging.info(f"Setting gain to {gain} dB.")
        self._gain = gain
        self._status = f"OPERATING - Freq: {self._frequency}MHz, Gain: {self._gain}dB"
        return True

    def get_idn(self) -> str:
        """Simulates the *IDN? query."""
        if not self._is_connected:
            return "No device connected."
        return f"Simulated RF Device, s/n:{self._device_id}, fw:1.0"

    @property
    def status(self) -> str:
        """Returns the current device status."""
        return self._status
