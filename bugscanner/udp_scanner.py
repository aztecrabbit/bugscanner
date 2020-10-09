import socket

from .bug_scanner import BugScanner


class UdpScanner(BugScanner):
	udp_server_host: str
	udp_server_port: int

	host_list: list

	def get_task_list(self):
		for host in self.host_list:
			yield {
				'host': host,
			}

	def task(self, payload):
		host = payload['host']

		G1 = self.logger.special_chars['G1']

		try:
			client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			client.settimeout(3)
			client.sendto(b'', (f'{host}.{self.udp_server_host}', int(self.udp_server_port)))
			client.recv(1024)

			self.log(f'{G1}{host}')

		except (OSError, socket.timeout):
			self.log(f'{host}')

		finally:
			client.close()
