from .bug_scanner import BugScanner


class CdnScanner(BugScanner):
	def __init__(self, task_list, port_list=None, method_list=None, threads=None):
		super().__init__(task_list, threads=threads)
		self._port_list = self.filter_list(port_list or ['80'])
		self._port_list = [int(x) for x in self._port_list]
		self._method_list = self.filter_list(method_list or ['head'])

	def request_connection_error(self):
		return 1

	def request_timeout(self):
		return 1

	def log_replace(self, *args):
		super().log_replace(f'{self.percentage_success():.3f}%', *args)

	def log_info(self, **kwargs):
		super().log("{method:<6}  {status_code:<4}  {server:<18}  {port:<4}  {hostname}".format(**kwargs))

	def get_task_list(self):
		self.log_info(method='method', status_code='code', server='server', port='port', hostname='hostname')
		self.log_info(method='------', status_code='----', server='------', port='----', hostname='--------')

		for method in self._method_list:
			for hostname in super().get_task_list():
				for port in self._port_list:
					yield {
						'method': method,
						'hostname': hostname,
						'port': port,
					}

	def task(self, payload):
		method = payload['method'].upper()
		hostname = payload['hostname']
		port = payload['port']
		url = self.get_url(hostname, port)

		data = {
			'method': method,
			'hostname': hostname,
			'port': port,
			'status_code': '',
			'server': '',
		}

		response = self.request(method, url, retry=1, timeout=3, allow_redirects=False)
		if response is not None:
			data = self.dict_merge(
				data, {
					'status_code': response.status_code,
					'server': response.headers.get('server', ''),
					'location': response.headers.get('location', ''),
				}
			)

			self.task_success(data)

		self.log_info(**data)
