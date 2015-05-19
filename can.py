import socket
import struct
import sys
import eventHook

class can:
    can_frame_fmt = "IB3x8s"
    can_device_name = 'can0'
    address_schema = {'MM1': 0x0000, 'DCC': 0xC000 } # KVP
    s = None
    vorwarts = 1
    ruckwarts = 2

    # constructor
    def __init__(self, name):
        self.can_device_name = name
        self.s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.s.bind((self.can_device_name,))

        self.onMessage = eventHook.EventHook()

        print("connected to CAN")

    # destructor
    def __del__(self):
        return






    def lok_funktion(self, loc_id, funktion, value):
        can_id = self.build_can_id(0, 0x06)
        data = struct.pack(">IBB", loc_id, int(funktion[1:]), value)
        self.send(can_id, data)
        return

    def lok_richtung(self, loc_id, richtung):
        can_id = self.build_can_id(0, 0x05)
        data = struct.pack(">IB", loc_id, richtung)
        self.send(can_id, data)
        return

    def lok_geschwindigkeit(self, loc_id, value):
        can_id = self.build_can_id(0, 0x04)
        data = struct.pack(">IH", loc_id, value)
        self.send(can_id, data)
        return

    def system_stopp(self):
        can_id = self.build_can_id(0, 0x00)
        data = struct.pack(">IB", 0, 0)
        self.send(can_id, data)
        return

    def system_go(self):
        can_id = self.build_can_id(0, 0x00)
        data = struct.pack(">IB", 0, 1)
        self.send(can_id, data)
        return

    def system_halt(self):
        can_id = self.build_can_id(0, 0x00)
        data = struct.pack(">IB", 0, 2)
        self.send(can_id, data)
        return

    def lok_nothalt(self, loc_id):
        can_id = self.build_can_id(0, 0x00)
        data = struct.pack(">IB", loc_id, 3)
        self.send(can_id, data)
        return







    def loc_id(self, protocol, nr):
        return self.address_schema[protocol] + nr

    def build_can_frame(self, can_id, data):
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        return struct.pack(self.can_frame_fmt, can_id, can_dlc, data)

    def build_can_id(self, response, command):
        b4 = 0x80 # turn on extended bit automatically
        b3 = 0x00
        b4 = (b4 | (command >> 7))
        b3 = (b3 | (command << 1))
        #b3 and response
        b2 = 0x0B # hash is constant magic number
        b1 = 0x3A
        return int.from_bytes(struct.pack("BBBB", b4, b3, b2, b1), byteorder='big')

    def send(self, can_id, data):
        can_frame = self.build_can_frame(can_id, data)
        self.send_frame(can_frame)  

    def send_frame(self, can_frame):
        self.s.send(can_frame)
