from sys import argv, exit
from datetime import datetime, timedelta
import socket, select, struct

#sample run: python proxy.py localhost 50001
# arguments: 
# 	1. host, 2. port
if len(argv) < 3:
	print("Invalid arguments\nrun: scriptname host port")
	exit()

class ChecksumProxy:

	def __init__(self, addr=argv[1], port=int(argv[2]), timeout=1):
		self.server = self.setupServer(addr, port)
		# sockets from which we expect to read
		self.inputs = [ self.server ]
		# wait for at least one of the sockets to be ready for processing
		self.timeout = timeout

		self.hashes = {}

	def setupServer(self, addr, port):
		# create a tcp/ip socket
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# bind the socket to the port
		server_address = (addr, port)
		server.bind(server_address)
		# listen for incoming connections
		server.listen(5)
		return server

	def handleInputs(self, readable):
		for sock in readable:
			if sock is self.server:
				self.handleNewConnection(sock)
			else:
				self.handleDataFromClient(sock)

	def handleNewConnection(self, sock):
		# a readable server socket is ready to accept a connection
		connection, client_address = sock.accept()
		connection.setblocking(0)
		self.inputs.append(connection)

	def handleDataFromClient(self, sock):
		data = sock.recv(1024)
		if data:
			msg = str(data, 'utf-8').split('|')
			# hint: msg contains 0) BE or KI 1) file id
			# in case of BE: 2) TTL 3) crc length 4) crc value
			request = msg[0]
			file_id = msg[1]
			if request == 'BE':
				ttl = int(msg[2])
				crc_length = int(msg[3])
				crc_value = msg[4]
				self.hashes[file_id] = {'length': crc_length, 'value': crc_value, 'ttl': ttl, 'timestamp': datetime.now()}
				sock.send(b'OK')

			elif request == 'KI':
				hash = self.hashes.get(file_id)
				if hash:
					# todo: check ttl
					if datetime.now() - hash['timestamp'] < timedelta(seconds=hash['ttl']):
						msg = str(hash['length']) + '|' + hash['value']
					else:
						msg = '0|'
				else:
					msg = '0|'
				sock.sendall(msg.encode('utf-8'))
			else:
				print('ERROR: invalid request')
		else:
			self.inputs.remove(sock)
			sock.close()

	def handleExceptionalCondition(self, exceptional):
		for sock in exceptional:
			print("Handling exceptional condition for " + str(sock.getpeername()))
			# stop listening for input on the connection
			self.inputs.remove(sock)
			sock.close()

	def handleConnections(self):
		# print("Waiting for connections...")
		while self.inputs:
			try:
				readable, writable, exceptional = select.select(self.inputs, [], self.inputs, self.timeout)
				if not (readable or writable or exceptional):
					# timed out, do some other work here
					continue

				self.handleInputs(readable)
				self.handleExceptionalCondition(exceptional)
			except KeyboardInterrupt:
				print(" Close the system")
				for c in self.inputs:
					c.close()
				self.inputs = []

checksumProxyServer = ChecksumProxy()
checksumProxyServer.handleConnections()