import os
import re
import sys
import ssl
import json
import queue
import socket
import argparse
import datetime
import requests
import threading

CN = "\033[K"
G1 = "\033[32;1m"
G2 = "\033[32;2m"
CC = "\033[0m"

lock = threading.RLock()

def get_value_from_list(data, index, default=""):
	try:
		return data[index]
	except IndexError:
		return default

def log(value):
	with lock:
		print(f"{CN}{value}{CC}")

def log_replace(value):
	sys.stdout.write(f"{CN}{value}{CC}\r")
	sys.stdout.flush()

class BugScanner:
	brainfuck_config = {
		"ProxyRotator": {
			"Port": "3080",
		},
		"Inject": {
			"Enable": True,
			"Type": 2,
			"Port": "8989",
			"Rules": {

			},
			"Payload": "",
			"MeekType": 0,
			"ServerNameIndication": "twitter.com",
			"Timeout": 5,
			"ShowLog": False,
		},
		"PsiphonCore": 4,
		"Psiphon": {
			"CoreName": "psiphon-tunnel-core",
			"Tunnel": 1,
			"Region": "",
			"Protocols": [
				"FRONTED-MEEK-HTTP-OSSH",
				"FRONTED-MEEK-OSSH",
			],
			"TunnelWorkers": 6,
			"KuotaDataLimit": 4,
			"Authorizations": [
				"",
			],
		},
	}
	scanned = {
		"direct": {},
		"ssl": {},
		"proxy": {},
	}

	def request(self, method, hostname, port, *args, **kwargs):
		try:
			url = ("https" if port == 443 else "http") + "://" + (hostname if port == 443 else f"{hostname}:{port}")
			log_replace(f"{method} {url}")
			return requests.request(method, url, *args, **kwargs)
		except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
			return None

	def resolve(self, hostname):
		try:
			cname, hostname_list, host_list = socket.gethostbyname_ex(hostname)
		except (socket.gaierror, socket.herror):
			return

		for i in range(len(hostname_list)):
			yield get_value_from_list(host_list, i, host_list[-1]), hostname_list[i]

		yield host_list[-1], cname

	def get_direct_response(self, method, hostname, port):
		if f"{hostname}:{port}" in self.scanned["direct"]:
			return None

		response = self.request(method.upper(), hostname, port, timeout=5, allow_redirects=False)
		if response is not None:
			status_code = response.status_code
			server = response.headers.get("server", "")
		else:
			status_code = ""
			server = ""

		self.scanned["direct"][f"{hostname}:{port}"] = {
			"status_code": status_code,
			"server": server,
		}
		return self.scanned["direct"][f"{hostname}:{port}"]

	def get_sni_response(self, hostname, deep):
		server_name_indication = ".".join(hostname.split(".")[0 - deep:])
		if server_name_indication in self.scanned["ssl"]:
			return None

		with lock:
			self.scanned["ssl"][server_name_indication] = None

		try:
			log_replace(server_name_indication)
			socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			socket_client.settimeout(5)
			socket_client.connect(("httpbin.org", 443))
			socket_client = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(
				socket_client, server_hostname=server_name_indication, do_handshake_on_connect=True
			)
		except:
			response = {
				"status": "",
				"server_name_indication": server_name_indication,
			}
		else:
			response = {
				"status": "True",
				"server_name_indication": server_name_indication,
			}
		finally:
			self.scanned["ssl"][server_name_indication] = response
			return self.scanned["ssl"][server_name_indication]

	def get_proxy_response(self, method, hostname, port, proxy):
		if f"{hostname}:{port}" in self.scanned["proxy"]:
			return None

		response = self.request(method.upper(), hostname, port, proxies={"http": "http://" + proxy, "https": "http://" + proxy}, timeout=5, allow_redirects=False)
		if response is None:
			return None

		if response.headers.get("location") == self.ignore_redirect_location:
			log(f"{self.proxy} -> {self.method} {response.url} ({response.status_code})")
			return None

		self.scanned["proxy"][f"{hostname}:{port}"] = {
			"proxy": self.proxy,
			"method": self.method,
			"url": response.url,
			"status_code": response.status_code,
			"headers": response.headers,
		}
		return self.scanned["proxy"][f"{hostname}:{port}"]

	def print_result(self, host, hostname, port=None, status_code=None, server=None, sni=None, color=""):
		if server in ["AkamaiGHost", "AkamaiNetStorage", "Varnish"] or sni == "True":
			color = G1
			if self.mode == "direct":
				whitelist_request = "*"
				if server in ["AkamaiGHost", "AkamaiNetStorage"]:
					whitelist_request = "akamai.net"
				elif server == "Varnish":
					whitelist_request = "fastly.net"
				if f"{whitelist_request}:{port}" not in self.brainfuck_config["Inject"]["Rules"]:
					self.brainfuck_config["Inject"]["Rules"][f"{whitelist_request}:{port}"] = []

				self.brainfuck_config["Inject"]["Rules"][f"{whitelist_request}:{port}"].append(f"{hostname}:{port}")

		if ((server == "AkamaiGHost" and status_code != 400) or
				(server == "Varnish" and status_code != 500) or
				(server == "AkamaiNetStorage")):
			color = G2

		host = f"{host:<15}"
		hostname = f"  {hostname}"
		sni = f"  {sni:<4}" if sni is not None else ""
		server = f"  {server:<20}" if server is not None else ""
		status_code = f"  {status_code:<4}" if status_code is not None else ""

		log(f"{color}{host}{status_code}{server}{sni}{hostname}")

	def print_result_proxy(self, response):
		if response is None:
			return

		data = []
		data.append(f"{response['proxy']} -> {response['method']} {response['url']} ({response['status_code']})\n")
		for key, val in response['headers'].items():
			data.append(f"|   {key}: {val}")
		data.append("|\n\n")

		log("\n".join(data))

	def scan(self):
		while True:
			for host, hostname in self.resolve(self.queue_hostname.get()):
				if self.mode == "direct":
					response = self.get_direct_response(self.method, hostname, self.port)
					if response is None:
						continue
					self.print_result(host, hostname, port=self.port, status_code=response["status_code"], server=response["server"])

				elif self.mode == "ssl":
					response = self.get_sni_response(hostname, self.deep)
					if response is None:
						continue
					self.print_result(host, response["server_name_indication"], sni=response["status"])

				elif self.mode == "proxy":
					response = self.get_proxy_response(self.method, hostname, self.port, self.proxy)
					self.print_result_proxy(response)

			self.queue_hostname.task_done()

	def start(self, hostnames):
		if self.mode == "direct":
			self.print_result("host", "hostname", status_code="code", server="server")
			self.print_result("----", "--------", status_code="----", server="------")
		elif self.mode == "ssl":
			self.print_result("host", "hostname", sni="sni")
			self.print_result("----", "--------", sni="---")

		self.queue_hostname = queue.Queue()
		for hostname in hostnames:
			self.queue_hostname.put(hostname)

		for _ in range(min(self.threads, self.queue_hostname.qsize())):
			thread = threading.Thread(target=self.scan)
			thread.daemon = True
			thread.start()

		self.queue_hostname.join()

		if self.output is not None and self.mode == "direct" and len(self.brainfuck_config["Inject"]["Rules"]):
			if os.name == "nt":
				self.brainfuck_config["Psiphon"]["CoreName"] += ".exe"
			with open(f"config.{self.output}.json", 'w', encoding='utf-8') as f:
				dump = json.dumps(self.brainfuck_config, indent=4, ensure_ascii=False)
				data = re.sub('\n +', lambda match: '\n' + '\t' * int((len(match.group().strip('\n')) / 4)), dump)
				f.write(data)

def main():
	parser = argparse.ArgumentParser(
		formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=52))
	parser.add_argument("filename", help="filename", type=str)
	parser.add_argument("-d", "--deep", help="subdomain deep", dest="deep", type=int, default=2)
	parser.add_argument("-m", "--mode", help="direct, proxy, ssl", dest="mode", type=str, default="direct")
	parser.add_argument("-o", "--output", help="output file name", dest="output", type=str)
	parser.add_argument("-p", "--port", help="target port", dest="port", type=int, default=80)
	parser.add_argument("-t", "--threads", help="threads", dest="threads", type=int, default=8)

	parser.add_argument("-I", "--ignore-redirect-location", help="ignore redirect location for --mode proxy", dest="ignore_redirect_location", type=str, default="")
	parser.add_argument("-M", "--method", help="http method", dest="method", type=str, default="HEAD")
	parser.add_argument("-P", "--proxy", help="proxy.example.com:8080", dest="proxy", type=str)

	args = parser.parse_args()
	if args.mode == "proxy" and not args.proxy:
		parser.print_help()
		return

	bugscanner = BugScanner()
	bugscanner.deep = args.deep
	bugscanner.ignore_redirect_location = args.ignore_redirect_location
	bugscanner.method = args.method.upper()
	bugscanner.mode = args.mode
	bugscanner.output = args.output
	bugscanner.port = args.port
	bugscanner.proxy = args.proxy
	bugscanner.threads = args.threads
	bugscanner.start(open(args.filename).read().splitlines())

if __name__ == "__main__":
	main()

