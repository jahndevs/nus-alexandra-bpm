import serial

# for mac
serial_port = serial.Serial('/dev/cu.SLAB_USBtoUART', 115200)

# for windows
# serial_port = serial.Serial('COM3', 115200)  # Windows

while True:
    raw_value = serial_port.readline().decode().strip()
    print(raw_value)