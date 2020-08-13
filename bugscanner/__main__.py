import argparse

from .cdn_scanner import CdnScanner
from .proxy_scanner import ProxyScanner


def get_arguments():
	parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=52))
	parser.add_argument(
		'filename',
		help='filename',
		type=str,
	)
	parser.add_argument(
		'-d',
		'--deep',
		help='subdomain deep',
		dest='deep',
		type=int,
		default=0,
	)
	parser.add_argument(
		'-m',
		'--mode',
		help='direct, proxy, ssl, udp',
		dest='mode',
		type=str,
		default='udp',
	)
	parser.add_argument(
		'-o',
		'--output',
		help='output file name',
		dest='output',
		type=str,
	)
	parser.add_argument(
		'-p',
		'--port',
		help='target port',
		dest='port',
		type=str,
		default='80',
	)
	parser.add_argument(
		'-t',
		'--threads',
		help='threads',
		dest='threads',
		type=int,
		default=0,
	)

	return parser.parse_args()


def main():
	arguments = get_arguments()

	threads = arguments.threads

	task_list = open(arguments.filename).read().splitlines()

	# scanner = CdnScanner(task_list, threads=threads)
	# scanner.start()

	scanner = ProxyScanner(task_list, ('proxy.jagoanssh.com', '80'), threads=threads)
	scanner.start()


if __name__ == '__main__':
	main()
