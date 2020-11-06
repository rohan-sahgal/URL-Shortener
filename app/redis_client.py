import redis


class Redis_Client:
  def __init__(self, host, db=0, socket_connect_timeout=2, socket_timeout=2):
    self._redis_server = redis.Redis(host=host, db=db, socket_connect_timeout=socket_connect_timeout, socket_timeout=socket_timeout)

  def insert(self, name, key, value):
    self._redis_server.hset(name, key, value)

  def get(self, name, key):
    return self._redis_server.hget(name, key)
