import serial


class IbcPkt:
    def __init__(self, attn=0, ttl=0, data_length=0, packet_id=0, data=bytearray()):
        self.attn = attn
        self.ttl = ttl
        self.data_length = data_length
        self.packet_id = packet_id
        self.data = data

    def pack(self):
        """Pack the packet fields into bytes."""
        header = ((self.attn & 0x0F) << 12) | ((self.ttl & 0x03) << 8) | \
                 ((self.data_length & 0x07) << 5) | (self.packet_id & 0x1F)
        header_bytes = header.to_bytes(2, byteorder='big')
        return header_bytes + self.data

    @classmethod
    def unpack(cls, packet_bytes):
        """Unpack bytes into an IbcPkt object."""
        header_bytes, data_bytes = packet_bytes[:2], packet_bytes[2:]
        header = int.from_bytes(header_bytes, byteorder='big')
        attn = (header >> 12) & 0x0F
        ttl = (header >> 8) & 0x03
        data_length = (header >> 5) & 0x07
        packet_id = header & 0x1F

        packet = cls(attn, ttl, data_length, packet_id)
        packet.data = bytearray(data_bytes)  # Set the data field
        return packet

    def __str__(self):
        return f"IbcPkt(attn=0x{self.attn:1X}, ttl=0x{self.ttl:1X}, data_length={self.data_length}, packet_id=0x{self.packet_id:2X}, data=0x{''.join([f'{byte:02X}' for byte in self.data])})"


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


def send_message(ser, packet):
    try:
        ser.write(packet.pack())
        print(f"Sent: {packet}")
    except serial.SerialException as e:
        print(f"Error communicating with the serial device: {e}")


def receive_response(ser):
    try:
        response_bytes = ser.read(12)
        response_packet = IbcPkt.unpack(response_bytes)
        print(f"Received: {response_packet}")
        return response_packet
    except serial.SerialException as e:
        print(f"Error communicating with the serial device: {e}")
        return None

def get_custom_packet():
    # Prompt the user for packet parameters
    attn = int(input("Enter ATTN (0-15): "), 16)
    ttl = int(input("Enter TTL (0-3): "), 16)
    data_length = int(input("Enter data length (0-7): "), 16)
    packet_id = int(input("Enter packet ID (0-31): "), 16)

    # Prompt the user for data bytes
    data = bytearray()
    for i in range(data_length):
        byte_value = int(input(f"Enter data byte {i + 1} (00-FF): "), 16)
        data.append(byte_value)

    custom_packet = IbcPkt(attn, ttl, data_length, packet_id, data)
    return custom_packet

def display_menu(messages, ser):
    while True:
        print("Select an option:")
        for i, (description, packet) in enumerate(messages):
            print(f"{i}: {description} - {packet}")
        print("c: Send Custom Packet")
        print("q: Quit")

        user_input = input("Enter your choice: ")

        if user_input == 'q':
            break
        elif user_input == 'c':
            custom_packet = get_custom_packet()
            send_message(ser, custom_packet)
            response = receive_response(ser)
            if response:
                print(f"Received: {response}")
        else:
            try:
                choice = int(user_input)
                if 0 <= choice < len(messages):
                    send_message(ser, messages[choice][1])
                    response = receive_response(ser)
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
                ("Set regA=5", IbcPkt(attn=0xF, ttl=2,
                                      data_length=4, packet_id=4,
                                      data=bytearray([0x00, 0x00, 0x00, 0x05]))),
                ("Set regA=33", IbcPkt(attn=0xF, ttl=2,
                                      data_length=4, packet_id=4,
                                      data=bytearray([0x00, 0x00, 0x00, 0x21]))),
                ("Set regB=0", IbcPkt(attn=0xF, ttl=2,
                                      data_length=4, packet_id=5,
                                      data=bytearray([0x00, 0x00, 0x00, 0x00]))),
                ("Set regB=37", IbcPkt(attn=0xF, ttl=2,
                                      data_length=4, packet_id=5,
                                      data=bytearray([0x00, 0x00, 0x00, 0x25]))),
                ("Set op rs1 + rs2", IbcPkt(attn=0xF, ttl=2,
                                            data_length=1, packet_id=0xC,
                                            data=bytearray([0x00]))),
                ("Set op rs1 - rs2", IbcPkt(attn=0xF, ttl=2,
                                            data_length=1, packet_id=0xC,
                                            data=bytearray([0x20]))),
                ("Set op rs1 ^ rs2", IbcPkt(attn=0xF, ttl=2,
                                            data_length=1, packet_id=0xC,
                                            data=bytearray([0x10]))),
                ("Set op rs1 | rs2", IbcPkt(attn=0xF, ttl=2,
                                            data_length=1, packet_id=0xC,
                                            data=bytearray([0x18]))),
                ("Set op rs1 & rs2", IbcPkt(attn=0xF, ttl=2,
                                            data_length=1, packet_id=0xC,
                                            data=bytearray([0x1C]))),
                ("CLK EDGE", IbcPkt(attn=0xF, ttl=3,
                                    data_length=1, packet_id=0xF,
                                    data=bytearray([0x00])))
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
