import select, socket, sys, struct
from random import randint

class BarkobaServer:

	def __init__(self, number, addr='localhost', port=10001, timeout=1):
		self.server = self.setupServer(addr, port)
		# sockets from which we expect to read
		self.inputs = [ self.server ]
		# wait for at least one of the sockets to be ready for processing
		self.timeout = timeout

		self.number = number
		print("The number is {}".format(number))
		self.is_end = False

	def setupServer(self, addr, port):
		# create a TCP/IP socket
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# bind the socket to the port
		server_address = (addr, port)
		server.bind(server_address)
		# listen for incoming connections
		server.listen(5)
		return server

	def handleNewConnection(self, sock):
		# a "readable" server socket is ready to accept a connection
		connection, client_address = sock.accept()
		connection.setblocking(0)
		self.inputs.append(connection)

	def getResponse(self, guess_operator, guess_number):
		if guess_operator == '>':
			response = 'I' if self.number > guess_number else 'N'
		elif guess_operator == '<':
			response = 'I' if self.number < guess_number else 'N'
		elif guess_operator == '=':
			response = 'Y' if self.number == guess_number else 'K'
		else:
			response = '?'
		return response

	def handleDataFromClient(self, sock):
		data = sock.recv(1024)
		if data:
			if self.is_end:
				sock.sendall(struct.Struct('c I').pack('V'.encode('utf-8'), 0))
				return

			packer = struct.Struct('c I')
			unpacked_data = packer.unpack(data)
			response = self.getResponse(unpacked_data[0].decode('utf-8'), unpacked_data[1])
			packed_response = packer.pack(response.encode('utf-8'), 0)
			sock.sendall(packed_response)
			if response == 'Y':
				print(str(sock.getpeername()) + " won!")
				self.is_end = True

		else:
			print(str(sock.getpeername()) + ' left')
			self.inputs.remove(sock)
			sock.close()

	def handleInputs(self, readable):
		for sock in readable:
			if sock is self.server:
				self.handleNewConnection(sock)
			else:
				self.handleDataFromClient(sock)

	def handleExceptionalCondition(self, exceptional):
		for sock in exceptional:
			print("Handling exceptional condition for " + str(sock.getpeername()))
			# stop listening for input on the connection
			self.inputs.remove(sock)
			sock.close()

	def handleConnections(self):
		while self.inputs:
			try:
				readable, writable, exceptional = select.select(self.inputs, [], self.inputs, self.timeout)
				if not (readable or writable or exceptional):
					# timed out, do some other work here
					continue

				self.handleInputs(readable)
				self.handleExceptionalCondition(exceptional)
				if len(self.inputs) == 1:
					self.number = randint(1, 100)
					print("Game over\n")
					print("The new number is: {}".format(self.number))
					self.is_end = False
			except KeyboardInterrupt:
				print("Close the system")
				for c in self.inputs:
					c.close()
				self.inputs = []

barkobaServer = BarkobaServer( randint(1, 100) )
barkobaServer.handleConnections()