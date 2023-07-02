

#! /usr/bin/env python


#@bicoinamical 2023 - Credit to @ottosch_ for parser

import sys, os, base64, requests
from bs4 import BeautifulSoup


txnid = input("what is the transaction id with the rom inscription?")
soup = "https://mempool.space/api/tx/{}/hex".format(txnid)
page = requests.get(soup)
file = page.text
raw = bytes.fromhex(file)


def read_bytes(n = 1):
	global pointer

	value = raw[pointer : pointer + n]
	pointer += n
	return value

def get_initial_position():
	inscription_mark = bytes.fromhex("0063036f7264")
	try:
		return raw.index(inscription_mark) + len(inscription_mark)
	except ValueError:
		print(f"No ordinal inscription found in transaction", file = sys.stderr)
		sys.exit(1)

def read_content_type():
	OP_1 = b"\x51"
  
	byte = read_bytes()
	if byte != OP_1:
		assert(byte == b'\x01')
		assert(read_bytes() == b'\x01')

	size = int.from_bytes(read_bytes(), "big")
	content_type = read_bytes(size)
	return content_type.decode("utf8")

def read_pushdata(opcode):
	int_opcode = int.from_bytes(opcode, "big")

	if 0x01 <= int_opcode <= 0x4b:
		return read_bytes(int_opcode)
	
	num_bytes = 0
	match int_opcode:
		case 0x4c:
			num_bytes = 1
		case 0x4d:
			num_bytes = 2
		case 0x4c:
			num_bytes = 4
		case _:
			print(f"Invalid push opcode {hex(int_opcode)} at position {pointer}", file = sys.stderr)
			sys.exit(1)
	
	size = int.from_bytes(read_bytes(num_bytes), "little")
	return read_bytes(size)
    
def write_file(data):
    filename = 'out.nes'
    f = open(filename, "wb")
    f.write(data)
    f.close()
    os.system('out.nes')
    os.remove('out.nes')
    
def main():
 

    global raw, pointer

    pointer = get_initial_position()
    content_type = read_content_type()
    print(f"Content type: {content_type}")
    assert(read_bytes() == b'\x00')
    
    data = bytearray()

    OP_ENDIF = b"\x68"
    opcode = read_bytes()
    while opcode != OP_ENDIF:
        chunk = read_pushdata(opcode)
        data.extend(chunk)
        opcode = read_bytes()
    print(f"Total size: {len(data)} bytes")
    write_file(data)
	
    print("\nDone")

main()
