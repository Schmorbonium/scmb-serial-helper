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
                input(f"Select a serial port (0 - {len(available_ports) - 1}): "))
            if 0 <= selection <= len(available_ports) - 1:
                return available_ports[selection][0]
            else:
                print("Invalid selection. Please choose a valid port number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def send_message(ser, message):
    try:
        ser.write(message)
        formatted_message = ''.join([f'{byte:02X}' for byte in message])
        print(f"Sent: 0x{formatted_message}")
    except serial.SerialException as e:
        print(f"Error communicating with the serial device: {e}")

def receive_response(ser):
    try:
        response = ser.read(12)
        return response
    except serial.SerialException as e:
        print(f"Error communicating with the serial device: {e}")
        return None

def display_menu(messages, ser):
    while True:
        print("Select an option:")
        for i, (description, hex_value) in enumerate(messages):
            formatted_hex_value = ''.join([f'{byte:02X}' for byte in hex_value])
            print(f"{i}: {description} - 0x{formatted_hex_value}")
        print("q: Quit")

        user_input = input("Enter your choice: ")

        if user_input == 'q':
            break

        try:
            choice = int(user_input)
            if 0 <= choice < len(messages):
                send_message(ser, messages[choice][1])
                response = receive_response(ser)
                if response:
                    formatted_response = ''.join([f'{byte:02X}' for byte in response])
                    print(f"Received: 0x{formatted_response}")
            else:
                print("Invalid option. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    available_ports = find_available_serial_ports()
    selected_port = select_serial_port(available_ports)
    ser = None

    if selected_port:
        try:
            ser = serial.Serial(selected_port, 115200, timeout=1)
            messages = [
                ("Set regA=5", b"\xF2\x84\x00\x00\x00\x00\x05"),
                ("Set regB=0", b"\xF2\x85\x00\x00\x00\x00\x00"),
                # Add more messages as needed
            ]
            display_menu(messages, ser)
        except serial.SerialException as e:
            print(f"Error opening the serial port: {e}")
        finally:
            if ser:
                ser.close()
    else:
        print("No serial port selected. Exiting.")
