import socket
import struct
import sys

can_frame_fmt = "IB3x8s"
can_device_name = 'can0'

def string_to_hex(s):
	return " ".join("{:02X}".format(c) for c in s)

def build_can_frame(can_id, data):
	can_dlc = len(data)
	data = data.ljust(8, b'\x00')
	return struct.pack(can_frame_fmt, can_id, can_dlc, data)

def dissect_can_frame(frame):
	can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
	return (can_id, can_dlc, data[:can_dlc])

def dissect_can_id(can_id):
        b4 = ((can_id >> 24) & 0xff) # 1st left most byte
        b3 = ((can_id >> 16) & 0xff) # 2nd left most byte
        
        extended_flag = bool((b4 & (1 << 7)))
        if (not extended_flag):
                print('not extended flag')
        remoteTransmissionRequest_flag = bool((b4 & (1 << 6)))
        if (remoteTransmissionRequest_flag):
                print('remoteTransmissionRequest_flag is set')
        error_flag = bool((b4 & (1 << 5)))
        if (error_flag):
                print('error_flag is set')

        prio     = (b4 & (~0xe1)) >> 1
        command  = (b4 & (~0xfe)) + (b3 >> 1)
        response = bool(b3 & (~0xfe))
        ahash    = (can_id & (~0xffff0000))
        return (prio, command, response, ahash)

if len(sys.argv) == 2:
        can_device_name = sys.argv[1] 
#	print('Provide CAN device name (can0, slcan0 etc.)')
#	sys.exit(0)

s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind((can_device_name,))

print('Device P Cmd  R   Hash   DLC  Data:')

while True:
	cf, addr = s.recvfrom(16)

	can_id, can_dlc, can_data = dissect_can_frame(cf)
	can_prio, can_command, can_response, can_hash = dissect_can_id(can_id)

	print('  %s %d 0x%02X %d (0x%04X) [%d]  %s' % (can_device_name, can_prio, can_command, can_response, can_hash, can_dlc, string_to_hex(can_data)))

