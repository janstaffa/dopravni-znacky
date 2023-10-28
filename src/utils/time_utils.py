import time

class StopWatch:
	def __init__(self):
		pass

	def start(self):
		self._startTime = time.time()
	
	def stop(self):
		currentTime = time.time()
		elapsed = currentTime - self._startTime
		elapsed = round(elapsed*1000, 2)
  
		print('-== Time elapsed - {}ms'.format(elapsed))