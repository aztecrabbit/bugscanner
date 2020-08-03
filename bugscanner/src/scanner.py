from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread

from .utils import log


class Scanner(ABC):
	def __init__(self, item_list, threads):
		super().__init__()
		self.item_list = self.filter_list(item_list)
		self.threads = threads or 8
		self.queue_item_list = Queue()

		self.item_total = 0
		self.item_scanned = 0
		self.item_list_success = []
		self.item_list_failed = []

		self.logger = log.Logger()

	def filter_list(self, item_list):
		filtered_item_list = []

		for item in item_list:
			if isinstance(item, str):
				item = item.strip()
				if item.startswith('#'):
					continue

			filtered_item_list.append(item)

		return list(set(filtered_item_list))

	def queue_add_item(self, item):
		self.queue_item_list.put(item)

	@abstractmethod
	def get_item_list(self):
		return self.item_list

	def start_thread(self):
		while True:
			item = self.queue_item_list.get()
			data = self.scan(item)
			self.scanned(data or item)
			self.queue_item_list.task_done()

	def start_threads(self):
		for _ in range(min(self.threads, self.queue_item_list.qsize()) or self.threads):
			Thread(target=self.start_thread, daemon=True).start()

	def start(self):
		try:
			for item in self.get_item_list():
				self.queue_item_list.put(item)
			self.item_total = self.queue_item_list.qsize()
			self.start_threads()
			self.join()
		except KeyboardInterrupt:
			with self.queue_item_list.mutex:
				self.keyboard_interrupt()
				self.queue_item_list.queue.clear()
		finally:
			self.complete()

	def join(self):
		self.queue_item_list.join()

	def percentage(self, data_count):
		return f'{(data_count / self.item_total) * 100:.3f}%'

	def percentage_scanned(self):
		return self.percentage(self.item_scanned)

	def percentage_success(self):
		return self.percentage(len(self.item_list_success))

	def percentage_failed(self):
		return self.percentage(len(self.item_list_failed))

	@abstractmethod
	def scan(self, item):
		pass

	@abstractmethod
	def scanned(self, data):
		self.item_scanned += 1

	@abstractmethod
	def success(self, data):
		self.item_list_success.append(data)

	@abstractmethod
	def failed(self, data):
		self.item_list_failed.append(data)

	def success_list(self):
		return self.item_list_success

	def failed_list(self):
		return self.item_list_failed

	@abstractmethod
	def keyboard_interrupt(self):
		self.logger.exception(
			'Keyboard Interrupted\n\n|   Ctrl-C again if not exiting automaticly\n|   Please wait...\n|\n'
		)

	@abstractmethod
	def complete(self):
		pass
