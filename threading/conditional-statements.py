#simple example checking the queue status when using threading method

import threading
import time
import random
import atexit

queue = []
MAX_ITEMS = 10#length of the queues
condition = threading.Condition()

class ProducerThread(threading.Thread):
    '''thread producer
	inheritage from the threading.Thread, overwrite the run function'''
	def run(self):

		numbers = range(5)
		global queue

		while True:
			condition.acquire()
			if len(queue) == MAX_ITEMS:
				print("Queue is full, producer is waiting")
				condition.wait()
				print("Space in queue, Consumer notified producer")
			number = random.choice(numbers)
			queue.append(number)
			print("Produced {}".format(number))
			condition.notify()
			condition.release()
			time.sleep(random.random())


class ConsumerThread(threading.Thread):
	'''thread consumer'''
	def run(self):
		global queue
		while True:
			condition.acquire()
			if not queue:
				print("Nothing in queue, consumer is waiting")
				condition.wait()
				print ("Producer added something to queue and notify the consumer")

			number = queue.pop(0)
			print("Consumed {}".format(number))
			condition.notify()
			condition.release()
			time.sleep(random.random())


producer = ProducerThread()
producer.daemon = True
producer.start()

consumer = ConsumerThread()
consumer.daemon = True
consumer.start()


def exit_handler():
	print("Terminating producer, consumer, mainApp...")


atexit.register(exit_handler)

while True:
	time.sleep(1)
