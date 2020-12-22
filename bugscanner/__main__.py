import argparse
import sys

from .direct_scanner import DirectScanner
from .ssl_scanner import SSLScanner
from .proxy_scanner import ProxyScanner
from .udp_scanner import UdpScanner


def get_arguments():
	parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=52))
	parser.add_argument(
		'filename',
		help='filename',
		type=str,
	)
	parser.add_argument(
		'--mode',
		help='mode',
		dest='mode',
		choices=('direct', 'proxy', 'ssl', 'udp'),
		type=str,
		default='direct',
	)
	parser.add_argument(
		'--method',
		help='method list',
		dest='method_list',
		type=str,
		default='head',
	)
	parser.add_argument(
		'--port',
		help='port list',
		dest='port_list',
		type=str,
		default='80',
	)
	parser.add_argument(
		'--proxy',
		help='proxy',
		dest='proxy',
		type=str,
		default='',
	)
	# parser.add_argument(
	# 	'--deep',
	# 	help='subdomain deep',
	# 	dest='deep',
	# 	type=int,
	# )
	parser.add_argument(
		'--output',
		help='output file name',
		dest='output',
		type=str,
	)
	parser.add_argument(
		'--threads',
		help='threads',
		dest='threads',
		type=int,
	)

	return parser.parse_args()


def main():
	arguments = get_arguments()

	method_list = arguments.method_list.split(',')
	host_list = open(arguments.filename).read().splitlines()
	port_list = arguments.port_list.split(',')
	proxy = arguments.proxy.split(':')

	if arguments.mode == 'direct':
		scanner = DirectScanner()

	elif arguments.mode == 'ssl':
		scanner = SSLScanner()

	elif arguments.mode == 'proxy':
		if not proxy or len(proxy) != 2:
			sys.exit('--proxy host:port')

		scanner = ProxyScanner()
		scanner.proxy = proxy

	elif arguments.mode == 'udp':
		scanner = UdpScanner()
		scanner.udp_server_host = 'bugscanner.tppreborn.my.id'
		scanner.udp_server_port = '8853'

	else:
		sys.exit('Not Available!')

	scanner.method_list = method_list
	scanner.host_list = host_list
	scanner.port_list = port_list
	scanner.threads = arguments.threads
	scanner.start()

	if arguments.output:
		with open(arguments.output, 'w+') as file:
			file.write('\n'.join([ str(x) for x in scanner.success_list() ]) + '\n')


if __name__ == '__main__':
	main()
