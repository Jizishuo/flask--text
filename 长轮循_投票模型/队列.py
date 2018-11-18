import queue

q = queue.Queue()

q.put('123')
val = q.get()
print(val)

val = q.get(timeout=30) #30秒
print(val) #报错