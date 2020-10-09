from .direct_scanner import DirectScanner


class ProxyScanner(DirectScanner):
	proxy = []

	def log_replace(self, *args):
		super().log_replace(':'.join(self.proxy), *args)

	def request(self, *args, **kwargs):
		proxies = {
			'http': self.get_url(*self.proxy),
			'https': self.get_url(*self.proxy),
		}

		return super().request(*args, proxies=proxies, **kwargs)
