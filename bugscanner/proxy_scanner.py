from .cdn_scanner import CdnScanner


class ProxyScanner(CdnScanner):
	def __init__(self, task_list, proxy, port_list=None, method_list=None, threads=None):
		super().__init__(task_list, port_list=port_list, method_list=method_list, threads=threads)
		self.proxy_host = str(proxy[0])
		self.proxy_port = int(proxy[1])

	def log_replace(self, *args):
		super().log_replace(f'{self.proxy_host}:{self.proxy_port}', *args)

	def request(self, *args, **kwargs):
		proxies = {
			'http': self.get_url(self.proxy_host, self.proxy_port),
			'https': self.get_url(self.proxy_host, self.proxy_port),
		}

		super().request(*args, proxies=proxies, **kwargs)
