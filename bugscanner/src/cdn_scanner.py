import requests

from .bug_scanner import BugScanner

class CdnScanner(BugScanner):
	def __init__(self, domain_list, port_list=None, method_list=None, threads=None):
		super().__init__(item_list=domain_list, port_list=port_list, threads=threads)
		self.method_list = self.filter_list(method_list or ['head'])

	def get_item_list(self):
		for (host, port) in self.get_host_port(self.item_list, self.port_list):
			for method in self.method_list:
				yield {
					'method': method.upper(),
					'host': host,
					'port': port,
				}

	def scan(self, item):
		method = item['method']
		host = item['host']
		port = item['port']
		url = self.get_url(host, port)

		try:
			response = requests.request(method, url, timeout=5, allow_redirects=False)
			self.success({
				'method': method,
				'host': host,
				'port': port,
				'url': url,
				'status_code': response.status_code,
				'server': response.headers.get('server'),
			})
		except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
			self.logger.log('FAIL', url)

	def keyboard_interrupt(self):
		super().keyboard_interrupt()

	def success(self, data):
		super().success(data)
		self.logger.success(data)

	def complete(self):
		# with open(real_path(f'{self.output_file_name}.txt'), 'w') as file:
		# 	for domain in self._success:
		# 		file.write(f'{domain}\n')
		for data in self.success_list():
			self.logger.success(data)
