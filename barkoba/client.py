import socket, sys, time, select, struct, random

class BarkobaClient:

	def __init__(self, serverAddr='localhost', serverPort=10001, timeout=1):
		self.setupClient(serverAddr, serverPort)
		self.low, self.high = 1, 100
		self.flip = random.getrandbits(1)

	def setupClient(self, serverAddr, serverPort):
		# create a tcp/ip socket
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#connect the socket to the port where the server is listening
		self.client.connect( (serverAddr, serverPort) )

	def handleResponse(self):
		data = self.client.recv(4096)
		if not data:
			print('\nDisconnected from server')
			sys.exit()
		else:
			unpacked_data = struct.Struct('c I').unpack(data)
			response = unpacked_data[0].decode('utf-8')
			if response == 'I':
				if self.flip:
					self.low = self.med + 1
				else:
					self.high = self.med - 1
			elif response == 'N':
				if self.flip:
					self.high = self.med
				else:
					self.low = self.med
			elif response == 'Y':
				print("I won!!!")
			elif response == 'K':
				print("I lose")
			elif response == 'V':
				print("Someone else won")
			else:
				print("Unknown response {}".format(response))
			self.flip = not self.flip
			return response == 'Y' or response == 'K' or response == 'V'

	def getRequest(self):
		if (self.low < self.high):
			self.med = int( (self.low + self.high) / 2)
			return '>' if self.flip else '<', self.med
		else:
			return '=', self.low


	def handleConnection(self):
		is_end = False
		while not is_end:
			request = self.getRequest()
			values = request[0].encode('utf-8'), request[1]
			print("Guess: x{}{}".format(request[0], self.med))
			packed_request = struct.Struct('c I').pack(*values)
			self.client.sendall(packed_request)
			is_end = self.handleResponse()
			try:
				time.sleep(random.randint(1, 5))
			except KeyboardInterrupt:
				print("\nExit")
				sys.exit()

barkobaClient = BarkobaClient()
barkobaClient.handleConnection()