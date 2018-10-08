import threading

counter_buffer = 0
counter_lock = threading.Lock()

COUNTER_MAX = 1000000


def consumer1_counter():
	global counter_buffer
	for i in range(COUNTER_MAX):
		counter_lock.acquire()s
		counter_buffer += 1
		counter_lock.release()


def consumer2_counter():
	global counter_buffer
	for i in range(COUNTER_MAX):
		counter_lock.acquire()
		counter_buffer += 1
		counter_lock.release()


t1 = threading.Thread(target=consumer1_counter)
t2 = threading.Thread(target=consumer2_counter)


t1.start()
t2.start()
#get the result run
t1.join()
t2.join()

print(counter_buffer)
