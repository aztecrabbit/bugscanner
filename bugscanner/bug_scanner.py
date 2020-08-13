import multithreading


class BugScanner(multithreading.MultiThreadRequest):
	def convert_host_port(self, host, port):
		return host + (f':{port}' if bool(port not in [80, 443]) else '')

	def get_url(self, host, port, uri=None):
		protocol = 'https' if port == 443 else 'http'

		return f'{protocol}://{self.convert_host_port(host, port)}' + (f'/{uri}' if uri is not None else '')
