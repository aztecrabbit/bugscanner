from .bug_scanner import BugScanner


class DirectScanner(BugScanner):
	method_list = []
	host_list = []
	port_list = []

	def log_info(self, **kwargs):
		for x in ['color', 'status_code', 'server']:
			kwargs[x] = kwargs.get(x, '')

		W2 = self.logger.special_chars['W2']
		G1 = self.logger.special_chars['G1']
		P1 = self.logger.special_chars['P1']
		CC = self.logger.special_chars['CC']

		if not kwargs['status_code']:
			kwargs['color'] = W2

		kwargs['CC'] = CC

		location = kwargs.get('location')

		if location:
			if location.startswith(f"https://{kwargs['host']}"):
				kwargs['status_code'] = f"{P1}{kwargs['status_code']:<4}"
			else:
				kwargs['host'] += f"{CC} -> {G1}{location}{CC}"

		messages = []

		for x in ['{method:<6}', '{status_code:<4}', '{server:<22}', '{port:<4}', '{host}']:
			messages.append(f'{{color}}{x}{{CC}}')

		super().log('  '.join(messages).format(**kwargs))

	def get_task_list(self):
		for method in self.filter_list(self.method_list):
			for host in self.filter_list(self.host_list):
				for port in self.filter_list(self.port_list):
					yield {
						'method': method.upper(),
						'host': host,
						'port': port,
					}

	def init(self):
		super().init()

		self.log_info(method='Method', status_code='Code', server='Server', port='Port', host='Host')
		self.log_info(method='------', status_code='----', server='------', port='----', host='----')

	def task(self, payload):
		method = payload['method']
		host = payload['host']
		port = payload['port']

		response = self.request(method, self.get_url(host, port), retry=1, timeout=3, allow_redirects=False)

		G1 = self.logger.special_chars['G1']
		G2 = self.logger.special_chars['G2']

		data = {
			'method': method,
			'host': host,
			'port': port,
		}

		if response is not None:
			color = ''
			status_code = response.status_code
			server = response.headers.get('server', '')
			location = response.headers.get('location', '')

			if server in ['AkamaiGHost']:
				if status_code == 400:
					color = G1
				else:
					color = G2

			elif server in ['Varnish']:
				if status_code == 500:
					color = G1

			elif server in ['AkamaiNetStorage']:
				color = G2

			data_success = {
				'color': color,
				'status_code': status_code,
				'server': server,
				'location': location,
			}

			data = self.dict_merge(data, data_success)

			self.task_success(data)

		self.log_info(**data)
