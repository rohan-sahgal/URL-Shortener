import redis


class Redis_Client:
  def __init__(host, port, db):
    self._redis_server = redis.Redis(host=host, port=port, db=db)

  def insert(name, key, value):
    self._redis_server.hset(name, key, value)

  def get(name, key):
    return self._redis_server.hget(name, key)
