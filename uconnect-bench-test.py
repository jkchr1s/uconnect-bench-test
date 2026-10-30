import can
import threading
import time

# UConnect Test Bench

# Configuration
COM_PORT='COM5' # check Device manager on Windows under COM ports
BITRATE = 125000 # 125000 is for IHS bus
VIN = "1C4HJXFGXHWXXXXXX" # Set your simulated VIN here

# Convert the vin to bytes
def get_vin_bytes(vin):
    # Pad or truncate to ensure exactly 17 bytes
    ascii_bytes = [ord(char) for char in vin[:17]]
    while len(ascii_bytes) < 17:
        ascii_bytes.append(0x00)
    return ascii_bytes

# convert the vin string to bytes
vin_b = get_vin_bytes(VIN)

messages = [
    # simulate ignition status
    can.Message(arbitration_id=0x122, data=[0x04, 0x02, 0x00, 0x00], is_extended_id=False),
    can.Message(arbitration_id=0x2FA, data=[0x00, 0x01, 0x00, 0x48, 0x00, 0x00, 0x00, 0x00], is_extended_id=False),
    can.Message(arbitration_id=0x3D3, data=[0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55], is_extended_id=False),
    
    # broadcast VIN across 3 frames
    can.Message(arbitration_id=0x3E8, data=[0x00] + vin_b[0:7], is_extended_id=False),
    can.Message(arbitration_id=0x3E8, data=[0x01] + vin_b[7:14], is_extended_id=False),
    can.Message(arbitration_id=0x3E8, data=[0x02] + vin_b[14:17] + [0x00, 0x00, 0x00, 0x00], is_extended_id=False)
]

# Extract transmission IDs so we can filter them out of the terminal feed
tx_ids = {msg.arbitration_id for msg in messages}

print(f"Connecting to CANable interface on {COM_PORT} at bitrate {BITRATE}")
bus = can.interface.Bus(interface='slcan', channel=COM_PORT, bitrate=BITRATE)

# function to create a worker thread to log messages (omitting our own)
def receive_worker(can_bus, tx_filter_set):
    print("Receiver thread started. Listening for IHS bus frames...")
    while True:
        try:
            # Wait up to 1 second for a message
            msg = can_bus.recv(timeout=1.0)
            if msg is not None:
                # Filter out our own transmitted frames so the screen isn't flooded
                if msg.arbitration_id not in tx_filter_set:
                    data_hex = " ".join(f"{b:02X}" for b in msg.data)
                    print(f"[RX] ID: {msg.arbitration_id:03X} | DLC: {msg.dlc} | Data: {data_hex}")
        except Exception as e:
            # Safely exit if the bus shuts down
            break

# start a receiving thread
rx_thread = threading.Thread(target=receive_worker, args=(bus, tx_ids), daemon=True)
rx_thread.start()

interval = 0.100 # 100 ms
print(f"Broadcasting wakeup sequence (VIN: {VIN}) every 100ms. Press Ctrl+C to stop.")

try:
    next_time = time.perf_counter()

    while True:
        # fire all messages
        for msg in messages:
            bus.send(msg)

        next_time += interval

        # sleep
        while time.perf_counter() < next_time:
            time.sleep(0.001)

except KeyboardInterrupt:
    print("\nStopped by user")
except can.CanError:
    print("Message failed to send")
finally:
    bus.shutdown()
    print("\nInterface disconnected.")