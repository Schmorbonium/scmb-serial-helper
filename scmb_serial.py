import serial


def find_available_serial_ports() -> list:
    available_ports = []
    try:
        from serial.tools import list_ports
        for port in list_ports.comports():
            available_ports.append((port.device, port.description))
    except ImportError:
        import serial.tools.list_ports
        for port in serial.tools.list_ports.comports():
            available_ports.append((port.device, port.description))
    return available_ports


def select_serial_port(available_ports):
    if not available_ports:
        print("No serial ports available.")
        return None

    print("Available serial ports:")
    for i, port in enumerate(available_ports):
        print(f"{i}: {port[0]} - {port[1]}")

    while True:
        try:
            selection = int(
                input(f"Select a serial port (0 - {len(available_ports)-1}): "))
            if 0 <= selection <= len(available_ports)-1:
                return available_ports[selection][0]
            else:
                print("Invalid selection. Please choose a valid port number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def send_hello_world(port):
    if port is None:
        return

    try:
        with serial.Serial(port, 115200, timeout=1) as ser:
            ser.write(b"hello world")
            print("Sent 'hello world' to the serial device.")
    except serial.SerialException as e:
        print(f"Error communicating with the serial device: {e}")


if __name__ == "__main__":
    available_ports = find_available_serial_ports()
    selected_port = select_serial_port(available_ports)
    send_hello_world(selected_port)
