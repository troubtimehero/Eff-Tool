import redis
import datetime

begin = datetime.datetime.now()

redis_pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=redis_pool)
mean = r.mget('hello', 'you', 'are', 'I', 'love', 'you', 'hi')
print(mean)
print(r.delete('a', 'foo', 'test'))
# mean = r.mget('hello', 'you', 'are', 'I', 'love', 'you')
# print(len(mean))
# print(mean)
print(r.keys())
# print(r.set('test', 'hahaha'))

end = datetime.datetime.now()
dur = end - begin
print(type(begin))
print(type(dur))
print(dur.total_seconds())
