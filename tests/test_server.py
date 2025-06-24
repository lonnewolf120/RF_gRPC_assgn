import pytest
from unittest.mock import MagicMock, patch
import grpc

# Add project root to path to allow imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from server.server import RFControlServicer
import rfcontrol_pb2

@pytest.fixture
def servicer():
    """Fixture to create an RFControlServicer with a mocked device."""
    with patch('server.rf_device.SimulatedRFDevice') as MockDevice:
        # The servicer __init__ creates an instance, so we mock the class
        mock_instance = MockDevice.return_value
        service = RFControlServicer()
        # Attach the mock instance to the service for inspection in tests
        service.device = mock_instance 
        yield service

def test_set_rf_settings_success(servicer):
    """Test the SetRFSettings RPC call with successful device operations."""
    # Arrange
    mock_device = servicer.device
    mock_device.set_frequency.return_value = True
    mock_device.set_gain.return_value = True
    mock_device.status = "OPERATING - Freq: 100.0MHz, Gain: 10.0dB"

    request = rfcontrol_pb2.RFConfig(
        frequency=100.0,
        gain=10.0,
        device_id="TEST01"
    )
    context = MagicMock()

    # Act
    response = servicer.SetRFSettings(request, context)

    # Assert
    mock_device.set_frequency.assert_called_once_with(100.0)
    mock_device.set_gain.assert_called_once_with(10.0)
    assert response.success is True
    assert response.device_status == "OPERATING - Freq: 100.0MHz, Gain: 10.0dB"
    context.set_code.assert_not_called()

def test_set_rf_settings_failure(servicer):
    """Test the SetRFSettings RPC call when a device operation fails."""
    # Arrange
    mock_device = servicer.device
    mock_device.set_frequency.return_value = False  # Simulate failure
    mock_device.set_gain.return_value = True
    mock_device.status = "CONNECTED - IDLE"

    request = rfcontrol_pb2.RFConfig(
        frequency=200.0,
        gain=15.0,
        device_id="TEST02"
    )
    context = MagicMock()

    # Act
    response = servicer.SetRFSettings(request, context)

    # Assert
    mock_device.set_frequency.assert_called_once_with(200.0)
    mock_device.set_gain.assert_called_once_with(15.0)
    assert response.success is False
    assert response.device_status == "CONNECTED - IDLE"
    context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
    context.set_details.assert_called_once()
