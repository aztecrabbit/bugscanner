import os
import sys
import ssl
import time
import queue
import socket
import argparse
import requests
import threading

lock = threading.RLock()

class Resolver:
	threads: int
	hostnames: list
	queue_hostnames: object

	def print_result(
			self, host: str, code: str, server: str, sni: str, hostname: str, color: str = ""):
		print(f"\033[K{color}{host:<15}  {code:<4}  {server:<18}  {sni:<4}  {hostname}\033[0m")

	def get_response(self, host: str) -> list:
		data = {
			"status_code": "",
			"server": "",
		}
		if self.mode != "brainfuck":
			return data
		while True:
			try:
				response = requests.head(f"http://{host}", timeout=10)
			except requests.exceptions.ConnectionError:
				return data
			except requests.exceptions.ReadTimeout:
				return data
			else:
				data["status_code"] = response.status_code
				data["server"] = response.headers.get("server", "")
				break

		return data

	def sni_scan(self, server_name_indication) -> str:
		if self.mode != "https":
			return ""
		try:
			socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			socket_client.settimeout(5)
			socket_client.connect(("httpbin.org", 443))
			socket_client = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(
				socket_client, server_hostname=server_name_indication, do_handshake_on_connect=True
			)
			# print(f"Certificate:\n\n{ssl.DER_cert_to_PEM_cert(socket_client.getpeercert(True))}")
		except:
			return "--"
		else:
			return "True"

	def add_result(self, host, code, server, sni, hostname):
		return {
			"host": host,
			"response": {
				"status_code": code,
				"server": server,
			},
			"sni": sni,
			"hostname": hostname,
		}

	def resolve(self, hostname: str):
		sys.stdout.write("\033[K" + hostname + "\r")
		sys.stdout.flush()

		try:
			response = socket.gethostbyname_ex(hostname)
		except socket.gaierror:
			return

		data = {}
		data["hostname"] = response[0]
		data["aliases_host"] = response[2]
		data["aliases_hostname"] = response[1]
		data["response"] = self.get_response(data["aliases_host"][-1])

		results = []
		index = 0

		for alias_host, alias_hostname in zip(data["aliases_host"], data["aliases_hostname"]):
			index += 1
			data["sni"] = ""
			if index > 1 or alias_hostname.startswith("www."):
				data["sni"] = self.sni_scan(alias_hostname)
			results.append(self.add_result(
				alias_host,
				data["response"]["status_code"],
				data["response"]["server"],
				data["sni"],
				alias_hostname,
			))

		data["sni"] = ""
		if len(data["aliases_hostname"]) or data["hostname"].startswith("www."):
			data["sni"] = self.sni_scan(data["hostname"])
		results.append(self.add_result(
			data["aliases_host"][-1],
			data["response"]["status_code"],
			data["response"]["server"],
			data["sni"],
			data["hostname"],
		))

		with lock:
			for data in results:
				color = ""
				if data["response"]["server"] in ["AkamaiGHost", "Varnish"]:
					color = "\033[32;1m"
				self.print_result(
					data["host"],
					data["response"]["status_code"],
					data["response"]["server"],
					data["sni"],
					data["hostname"],
					color
				)
	
	def run(self):
		while True:
			self.resolve(self.queue_hostnames.get())
			self.queue_hostnames.task_done()

	def start(self):
		self.queue_hostnames = queue.Queue()
		for hostname in self.hostnames:
			self.queue_hostnames.put(hostname)

		self.print_result("host", "code", "server", "sni", "hostname")
		self.print_result("----", "----", "------", "---", "--------")
		
		for _ in range(min(self.threads, self.queue_hostnames.qsize())):
			thread = threading.Thread(target=self.run, args=())
			thread.daemon = True
			thread.start()

		self.queue_hostnames.join()

def main():
	parser = argparse.ArgumentParser(
		formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=52))
	parser.add_argument("filename", help="hostnames file", type=str)
	parser.add_argument("-m", "--mode", help="brainfuck (default), http, https",
		dest="mode", type=str, default="brainfuck")
	parser.add_argument("-t", "--threads", help="threads", dest="threads", type=int, default=8)

	args = parser.parse_args()
	args.threads = 8 if not args.threads else args.threads
	if args.mode not in ["brainfuck", "direct", "http", "https"]:
		parser.print_help()
		sys.exit()

	resolver = Resolver()
	resolver.mode = args.mode
	resolver.threads = args.threads
	resolver.hostnames = open(args.filename).read().splitlines()
	resolver.start()
	
if __name__ == "__main__":
	main()

