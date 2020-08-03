from .scanner import Scanner


class BugScanner(Scanner):
	def __init__(self, item_list, port_list=None, threads=None):
		super().__init__(item_list, threads=threads)
		self.port_list = self.filter_list(port_list or [80])

	def get_host_port(self, host_list, port_list):
		for host in host_list:
			for port in port_list:
				yield (host, port)

	def convert_host_port(self, host, port):
		return host + (f':{port}' if bool(port not in [80, 443]) else '')

	def get_url(self, host, port):
		protocol = 'https' if port == 443 else 'http'

		return f'{protocol}://{self.convert_host_port(host, port)}'
