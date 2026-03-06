# serial_comm.py
import serial
import serial.tools.list_ports
import time
import logging

class SerialComm:
    def __init__(self, logger: logging.Logger, use_bluetooth=False):
        self.logger = logger
        self.ser = None
        self.use_bluetooth = use_bluetooth

    def connect(self, config=None):
        """
        Connect to the Arduino/ESP32 serial port.
        If config is None, tries to auto-detect.
        """
        if config is None:
            config = {"serial": {"port": None, "baud": 9600},
                      "bluetooth": {"baud": 9600}}
        
        if self.use_bluetooth:
            port = config.get("bluetooth_port", None)
            baud = config["bluetooth"]["baud"]
        else:
            port = config["serial"].get("port")
            baud = config["serial"].get("baud", 9600)

        # Auto-detect if port is None
        if not port:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            if not ports:
                self.logger.error("No serial ports found")
                return
            port = ports[0]  # pick the first one
            self.logger.info(f"Auto-detected serial port: {port}")

        try:
            self.ser = serial.Serial(port, baud, timeout=0, write_timeout=0)
            time.sleep(2)  # allow Arduino to reset
            self.logger.info(f"Connected to {port} at {baud} baud")
        except Exception as e:
            self.logger.error(f"Failed to connect to {port}: {e}")
            self.ser = None

    def send(self, packet: str):
        """
        Send control packet. Non-blocking, safe if COM is open elsewhere.
        """
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(packet.encode())
                self.ser.flush()
            except Exception as e:
                self.logger.warning(f"Failed to send packet: {e}")
        else:
            self.logger.debug("Serial not connected, skipping packet")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.logger.info("Serial connection closed")
