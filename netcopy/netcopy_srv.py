from sys import argv, exit
import socket, zlib
# sample run: python server.py localhost 50000 localhost 50001 01 recieved_file
# arguments: 
# 	1. host, 2. port
# 	3. cksum host, 4. cksum port
# 	5. file id, 6. file path and name
if len(argv) < 7:
	print("Invalid argument list\nrun: scriptname server-host server-port cksum-server-host cksum-server-port file-id file-path-and-name")
	exit()

host = argv[1]
port = int(argv[2])

s = socket.socket()
s.bind((host, port))
s.listen(5)

# print('Server listening....')

# get file from client and calculate crc simultaneously
conn, addr = s.accept()	 
# print('Got connection from', addr)

with open(argv[6], 'wb') as f:
	data = conn.recv(1024)
	crcvalue = 0
	while data: 
		f.write(data)
		crcvalue = zlib.crc32(data, crcvalue)
		data = conn.recv(1024)

# print('File recieved')
crcvalue = str(crcvalue)
conn.close()

# get CRC from proxy
proxy_conn = socket.socket()
proxy_conn.connect((argv[3], int(argv[4])))
file_id = argv[5]
msg = 'KI|' + argv[5]
proxy_conn.sendall(msg.encode('utf-8'))
data = proxy_conn.recv(1024)

msg = str(data, 'utf-8').split('|')
if int(msg[0]) == 0:
	print('CSUM CORRUPTED')
elif int(msg[0]) != len(crcvalue):
	print('CCSUM CORRUPTED')
elif msg[1] != crcvalue:
	print('CSUM CORRUPTED')
else:
	print('CSUM OK')