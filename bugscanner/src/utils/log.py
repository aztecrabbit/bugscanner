import sys
from threading import RLock
# from loguru import logger

lock = RLock()

special_chars = {
	'R1': '\033[31;1m',
	'R2': '\033[31;2m',
	'G1': '\033[32;1m',
	'G2': '\033[32;2m',
	'Y1': '\033[33;1m',
	'Y2': '\033[33;2m',
	'B1': '\033[34;1m',
	'B2': '\033[34;2m',
	'P1': '\033[35;1m',
	'P2': '\033[35;2m',
	'C1': '\033[36;1m',
	'C2': '\033[36;2m',
	'CC': '\033[0m',
	'CN': '\033[2K',
	'CR': '\r',
}

class Logger:
	def replace(self, message: str):
		with lock:
			sys.stdout.write(f"{special_chars['CN']}{message}{special_chars['CC']}{special_chars['CR']}")
			sys.stdout.flush()

	def log(self, message, color=special_chars['G2']):
		with lock:
			print(f"{special_chars['CR']}{special_chars['CN']}{color}{message}{special_chars['CC']}")

	def failed(self, message):
		self.log(message, color=special_chars['G2'])

	def success(self, message):
		self.log(message, color=special_chars['G1'])

	def exception(self, message):
		self.log(message, color=special_chars['R1'])




# class Logger:
# 	def __init__(self):
# 		super().__init__()
# 		self.logger = logger
# 		self.logger.remove()
# 		self.logger.configure(extra={
# 			'CR': special_chars['CR'],
# 			'CC': special_chars['CC'],
# 		})
# 		self.logger.add(
# 			sys.stderr,
# 			format=' '.join([
# 				'{extra[CR]}{extra[color]}[{time:HH:mm:ss.SSS}]{extra[CC]}',
# 				'<magenta>::</magenta>',
# 				'{extra[color]}{level}{extra[CC]}',
# 				'<magenta>::</magenta>',
# 				'{extra[color]}{extra[status]}{extra[CC]}',
# 				'<magenta>::</magenta>',
# 				'{extra[color]}{message}{extra[CC]}',
# 			]),
# 			level='DEBUG',
# 			colorize=True,
# 		)

# 	def replace(self, message: str):
# 		sys.stdout.write(f"{special_chars['CN']}{message}{special_chars['CC']}{special_chars['CR']}")
# 		sys.stdout.flush()

# 	def log(self, message: str, status: str = 'INFO', level: str = 'INFO', color: str = special_chars['G2']):
# 		self.logger.bind(color=color, status=status).log(level, message)

# 	def failed(self, message: str):
# 		self.log(message, color=special_chars['G2'], level='ERROR')

# 	def success(self, message: str):
# 		self.log(message, color=special_chars['G1'], level='SUCCESS')

# 	def exception(self, message: str):
# 		self.log(message, color=special_chars['R1'], level='ERROR')
