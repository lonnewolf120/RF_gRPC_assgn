import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
import grpc

# Import gRPC client logic
import rfcontrol_pb2
import rfcontrol_pb2_grpc

logging.basicConfig(level=logging.INFO)

class RFControlUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RF Device Control")
        self.geometry("400x400")

        self.create_widgets()

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self, text="RF Settings", padding="10")
        input_frame.pack(padx=10, pady=10, fill="x")

        # Frequency
        ttk.Label(input_frame, text="Frequency (MHz):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.freq_entry = ttk.Entry(input_frame)
        self.freq_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.freq_entry.insert(0, "915.0")

        # Gain
        ttk.Label(input_frame, text="Gain (dB):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.gain_entry = ttk.Entry(input_frame)
        self.gain_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.gain_entry.insert(0, "20.0")

        # Device ID
        ttk.Label(input_frame, text="Device ID:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.id_entry = ttk.Entry(input_frame)
        self.id_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.id_entry.insert(0, "DEV001")

        # Server Address
        ttk.Label(input_frame, text="Server Address:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.server_entry = ttk.Entry(input_frame)
        self.server_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.server_entry.insert(0, "localhost:50051")

        input_frame.columnconfigure(1, weight=1)

        # Control Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5)

        self.set_button = ttk.Button(button_frame, text="Set RF Settings", command=self.set_rf_settings)
        self.set_button.pack(side="left", padx=5)

        self.get_status_button = ttk.Button(button_frame, text="Get Device Status", command=self.get_device_status)
        self.get_status_button.pack(side="left", padx=5)

        # Response Frame
        response_frame = ttk.LabelFrame(self, text="Server Response", padding="10")
        response_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.response_text = tk.Text(response_frame, height=8, state="disabled")
        self.response_text.pack(fill="both", expand=True)

        # Status Bar
        self.status_label = ttk.Label(self, text="Ready", relief="sunken", anchor="w")
        self.status_label.pack(side="bottom", fill="x")

    def set_rf_settings(self):
        self.status_label.config(text="Sending request...")
        self.set_button.config(state="disabled")
        self.clear_response_text()

        try:
            frequency = float(self.freq_entry.get())
            gain = float(self.gain_entry.get())
            device_id = self.id_entry.get()
            server_addr = self.server_entry.get()
        except ValueError:
            messagebox.showerror("Input Error", "Frequency and Gain must be valid numbers.")
            self.status_label.config(text="Error: Invalid input")
            self.set_button.config(state="normal")
            return

        # Run the gRPC call in a separate thread to keep the UI responsive
        threading.Thread(
            target=self._send_grpc_request,
            args=(frequency, gain, device_id, server_addr)
        ).start()

    def get_device_status(self):
        self.status_label.config(text="Getting device status...")
        self.get_status_button.config(state="disabled")
        self.clear_response_text()

        device_id = self.id_entry.get()
        server_addr = self.server_entry.get()

        threading.Thread(
            target=self._get_status_grpc_request,
            args=(device_id, server_addr)
        ).start()

    def _send_grpc_request(self, frequency, gain, device_id, server_addr):
        try:
            with grpc.insecure_channel(server_addr) as channel:
                stub = rfcontrol_pb2_grpc.RFControlStub(channel)
                response = stub.SetRFSettings(
                    rfcontrol_pb2.RFConfig(
                        frequency=frequency, gain=gain, device_id=device_id
                    )
                )
                self.after(0, self.display_response, response.success, response.device_status)
        except grpc.RpcError as e:
            self.after(0, self.display_error, f"RPC failed: {e.code()} - {e.details()}")
        except Exception as e:
            self.after(0, self.display_error, f"An unexpected error occurred: {e}")
        finally:
            self.after(0, lambda: self.set_button.config(state="normal"))
            self.after(0, lambda: self.get_status_button.config(state="normal"))

    def _get_status_grpc_request(self, device_id, server_addr):
        try:
            with grpc.insecure_channel(server_addr) as channel:
                stub = rfcontrol_pb2_grpc.RFControlStub(channel)
                response = stub.GetDeviceStatus(
                    rfcontrol_pb2.DeviceStatusRequest(device_id=device_id)
                )
                self.after(0, self.display_response, response.success, response.device_status)
        except grpc.RpcError as e:
            self.after(0, self.display_error, f"RPC failed: {e.code()} - {e.details()}")
        except Exception as e:
            self.after(0, self.display_error, f"An unexpected error occurred: {e}")
        finally:
            self.after(0, lambda: self.set_button.config(state="normal"))
            self.after(0, lambda: self.get_status_button.config(state="normal"))

    def display_response(self, success, status):
        self.response_text.config(state="normal")
        self.response_text.insert(tk.END, f"Success: {success}\n")
        self.response_text.insert(tk.END, f"Device Status: {status}\n")
        self.response_text.config(state="disabled")
        self.status_label.config(text="Request complete")

    def display_error(self, error_message):
        self.response_text.config(state="normal")
        self.response_text.insert(tk.END, f"Error: {error_message}\n")
        self.response_text.config(state="disabled")
        self.status_label.config(text="Error during request")
        messagebox.showerror("Error", error_message)

    def clear_response_text(self):
        self.response_text.config(state="normal")
        self.response_text.delete(1.0, tk.END)
        self.response_text.config(state="disabled")

if __name__ == "__main__":
    app = RFControlUI()
    app.mainloop()
