from .direct_scanner import DirectScanner


class ProxyScanner(DirectScanner):
	proxy = []

	def log_replace(self, *args):
		super().log_replace(':'.join(self.proxy), *args)

	def request(self, *args, **kwargs):
		proxy = self.get_url(self.proxy[0], self.proxy[1])

		return super().request(*args, proxies={'http': proxy, 'https': proxy}, **kwargs)
