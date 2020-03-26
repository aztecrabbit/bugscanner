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

def log(value: str):
	with lock:
		print("\033[K" + value + "\033[0m")

def log_replace(value: str):
	sys.stdout.write("\033[K" + value + "\r")
	sys.stdout.flush()

def get_data_list(data: list, index: int, default: str = "") -> str:
	try:
		return data[index]
	except IndexError:
		return default

class Resolver:
	mode: str
	threads: int
	hostnames: list
	hostname_deep: int
	server_name_indication_scanned: list = []

	def add_data(self, host: str, hostname: str, status_code: str = "", server: str = "", sni: str = ""):
		return {
			"host": host,
			"hostname": hostname,
			"status_code": status_code,
			"server": server,
			"sni": sni,
		}

	def print_data_list(self, data_list: list):
		with lock:
			for data in data_list:
				color = ""
				if self.mode == "brainfuck":
					if data["server"] in ["AkamaiGHost", "Varnish"]:
						color = "\033[32;1m" # Green
					log(color + f"{data['host']:<15}  {data['status_code']:<4}  {data['server']:<20}  {data['hostname']}")
				elif self.mode in ["https", "ssl", "sni"]:
					if data["sni"] == "True":
						color = "\033[32;1m" # Green
					log(color + f"{data['host']:<15}  {data['sni']:<4}  {data['hostname']}")

	def scan_server_name_indication(self, hostname: str):
		if self.mode not in ["https", "ssl", "sni"]:
			return ""

		with lock:
			server_name_indication = ".".join(hostname.split(".")[0 - self.hostname_deep:])
			if server_name_indication in self.server_name_indication_scanned:
				return ""
			self.server_name_indication_scanned.append(server_name_indication)

		try:
			socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			socket_client.settimeout(10)
			socket_client.connect(("httpbin.org", 443))
			socket_client = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(
				socket_client, server_hostname=server_name_indication, do_handshake_on_connect=True
			)
		except:
			return "--"
		else:
			return "True"

	def get_http_response(self, host: str) -> (str, str):
		if self.mode != "brainfuck":
			return "", ""

		while True:
			try:
				response = requests.head(f"http://{host}", timeout=10)
			except requests.exceptions.ConnectionError:
				return "", ""
			except requests.exceptions.ReadTimeout:
				return "", ""
			else:
				return response.status_code, response.headers.get("server", "")

	def resolve(self, hostname: str):
		try:
			log_replace(hostname)
			name, aliaslist, addresslist = socket.gethostbyname_ex(hostname)
		except socket.gaierror:
			return

		for i in range(len(aliaslist)):
			alias_hostname = aliaslist[i]
			alias_host = get_data_list(addresslist, i, addresslist[-1])
			yield alias_host, alias_hostname

		yield addresslist[-1], name

	def run(self):
		while True:
			data_list = []
			last_host = ""
			status_code, server = "", ""
			for host, hostname in self.resolve(self.queue_hostname.get()):
				if host != last_host:
					last_host = host
					status_code, server = self.get_http_response(host)
				if not host and not status_code and not server:
					continue
				sni = self.scan_server_name_indication(hostname)
				data_list.append(self.add_data(host, hostname, status_code, server, sni))
			self.print_data_list(data_list)
			self.queue_hostname.task_done()

	def start(self):
		self.queue_hostname = queue.Queue()
		for hostname in self.hostnames:
			self.queue_hostname.put(hostname)

		self.print_data_list([
			self.add_data("host", "hostname", "code", "server", "sni"),
			self.add_data("----", "--------", "----", "------", "---"),
		])

		for _ in range(min(self.threads, self.queue_hostname.qsize())):
			thread = threading.Thread(target=self.run, args=())
			thread.daemon = True
			thread.start()

		self.queue_hostname.join()

def main():
	parser = argparse.ArgumentParser(
		formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=52))
	parser.add_argument("filename", help="hostnames file", type=str)
	parser.add_argument("-m", "--mode", help="brainfuck (default), http, https, ssl, sni",
		dest="mode", type=str, default="brainfuck")
	parser.add_argument("-d", "--deep", help="hostname deep for ssl mode", dest="hostname_deep", type=int, default=2)
	parser.add_argument("-t", "--threads", help="threads", dest="threads", type=int, default=8)

	args = parser.parse_args()
	args.threads = 8 if not args.threads else args.threads
	if args.mode not in ["brainfuck", "http", "https", "ssl", "sni"]:
		parser.print_help()
		sys.exit()

	resolver = Resolver()
	resolver.mode = args.mode
	resolver.threads = args.threads
	resolver.hostnames = open(args.filename).read().splitlines()
	resolver.hostname_deep = args.hostname_deep if args.hostname_deep > 1 else 2
	resolver.start()
	
if __name__ == "__main__":
	main()

