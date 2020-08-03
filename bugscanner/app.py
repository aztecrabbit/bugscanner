import argparse

from src.udp_scanner import UdpScanner
# from src.cdn_scanner import CdnScanner


def filter_port(str_port_list):
	port_list = str_port_list.split(',')
	port_list_filtered = []

	for port in port_list:
		port_list_filtered.append(int(port))

	return port_list_filtered


def main():
	parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=52))
	parser.add_argument('filename', help='filename', type=str)
	parser.add_argument('-d', '--deep', help='subdomain deep', dest='deep', type=int, default=0)
	parser.add_argument('-m', '--mode', help='direct, proxy, ssl, udp', dest='mode', type=str, default='direct')
	parser.add_argument('-o', '--output', help='output file name', dest='output', type=str)
	parser.add_argument('-p', '--port', help='target port', dest='port', type=str, default='80')
	parser.add_argument('-t', '--threads', help='threads', dest='threads', type=int, default=0)
	arguments = parser.parse_args()

	domain_list = open(arguments.filename).read().splitlines()
	# domain_list = ['instagram.fcgk8-1.fna.fbcdn.net']

	if arguments.mode not in ['direct', 'proxy', 'ssl', 'udp']:
		print('mode error')
		return

	mode = arguments.mode

	deep = arguments.deep if arguments.deep >= 2 else 2

	port_list = filter_port(arguments.port)

	if mode == 'udp':
		threads = arguments.threads or 32

		udp_scanner = UdpScanner(
			udp_server=('205.quantumtunnel.xyz', 8383),
			domain_list=domain_list,
			threads=threads,
		)
		udp_scanner.output_file_name = arguments.output or 'udp-results'
		udp_scanner.start()

	# elif mode == 'direct':
	# 	threads = arguments.threads or 8

	# 	cdn_scanner = CdnScanner(
	# 		domain_list=domain_list,
	# 		port_list=port_list,
	# 		method_list=['head'],
	# 		threads=threads,
	# 	)
	# 	cdn_scanner.output_file_name = output_file_name
	# 	cdn_scanner.start()

	else:
		print(f'mode "{mode}" not found, try again next version')
		return


if __name__ == '__main__':
	main()
