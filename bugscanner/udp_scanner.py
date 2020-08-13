import os
import sys
import socket
# import threading

from .bug_scanner import BugScanner

# lock = threading.RLock()

# CN = '\033[K'
# CC = '\033[0m'
# G1 = '\033[32;1m'


def real_path(name: str) -> str:
	return os.path.dirname(os.path.abspath(sys.argv[0])) + '/' + name


# def log(value: str):
# 	with lock:
# 		print(f'{CN}{value}{CC}')

# def log_replace(value: str):
# 	sys.stdout.write(f'{CN}{value}{CC}\r')
# 	sys.stdout.flush()


class UdpScanner(BugScanner):
	output_file_name: str

	def __init__(self, udp_server, domain_list, threads):
		super().__init__(item_list=domain_list, threads=threads)
		self.udp_server_host = str(udp_server[0])
		self.udp_server_port = int(udp_server[1])

	def get_item_list(self):
		return super().get_item_list()

	def scan(self, domain):
		self.logger.replace(
			' - '.join([
				f'{self.item_scanned} of {self.item_total}',
				self.percentage_scanned(),
				self.percentage_success(),
				self.percentage_failed(),
				domain,
			])
		)

		target = f'{domain}.{self.udp_server_host}'

		try:
			client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			client.settimeout(3)
			client.sendto(b'', (target, self.udp_server_port))
			client.recv(1024)
			self.success(domain)
		except (OSError, socket.timeout):
			self.failed(domain)
		finally:
			client.close()

	def scanned(self, data):
		super().scanned(data)

	def keyboard_interrupt(self):
		super().keyboard_interrupt()

	def success(self, domain):
		super().success(domain)
		self.logger.success(domain)

	def failed(self, domain):
		super().failed(domain)
		self.logger.failed(domain)

	def complete(self):
		super().complete()

		output_file = real_path(f'{self.output_file_name}.txt')
		with open(output_file, 'w') as file:
			for domain in self.item_list_success:
				file.write(f'{domain}\n')

		self.logger.success(output_file)
