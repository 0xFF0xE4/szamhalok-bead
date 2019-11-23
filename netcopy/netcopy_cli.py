from sys import argv, exit
import socket, zlib

# sample run: python client.py localhost 50000 localhost 50001 01 lorem.txt
# arguments: 
# 	1. server host, 2. server port
# 	3. cksum host, 4. cksum port
# 	5. file id, 6. file path and name
if len(argv) < 7:
	print("Invalid argument list\nrun: scriptname server-host server-port cksum-server-host cksum-server-port file-id file-path-and-name")
	exit()

server_conn = socket.socket()
server_conn.connect((argv[1], int(argv[2])))

proxy_conn = socket.socket()
proxy_conn.connect((argv[3], int(argv[4])))

# send file to the server and calculate crc simultaneously
with open(argv[6], 'rb') as f:
	data = f.read(1024)
	crcvalue = 0
	while data:
		server_conn.send(data)
		crcvalue = zlib.crc32(data, crcvalue)
		data = f.read(1024)
server_conn.close()

# send crc to proxy
crc = str(crcvalue)
msg = ('BE|' + argv[5] + '|60|' + str(len(crc)) + '|' + crc).encode('utf-8')
proxy_conn.sendall(msg)
data = proxy_conn.recv(1024)
print(data)