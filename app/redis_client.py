import redis


class Redis_Client:
  def __init__(self, host, db=0, socket_connect_timeout=2, socket_timeout=2):
    self._host = host
    self._db = db
    self._socket_connect_timeout = socket_connect_timeout
    self._socket_timeout = socket_timeout
    connect(host, db, socket_connect_timeout, socket_timeout)
  
  def connect():
    try:
      self._redis_server = redis.Redis(host=host, db=db, socket_connect_timeout=socket_connect_timeout, socket_timeout=socket_timeout)
    except Exception as e:
      self._redis_server = None
      print('REDIS ERROR: Cannot connect to Redis. ' + str(e))

  def insert(self, name, key, value):
    if self._redis_server != None:
      self._redis_server.hset(name, key, value)
    else:
      connect(self._host, self._db, self._socket_connect_timeout, self._socket_timeout)
      if self._redis_server != None:
        self._redis_server.hset(name, key, value)
  
  def insert_list(self, name, key, value):
    if self._redis_server != None:
      self._redis_server.lpush(name, '{}:::{}'.format(key, value))
    else:
      connect(self._host, self._db, self._socket_connect_timeout, self._socket_timeout)
      if self._redis_server != None:
        self._redis_server.lpush(name, '{}:::{}'.format(key, value))

  def get(self, name, key):
    if self._redis_server != None:
      return self._redis_server.hget(name, key)
    else:
      connect(self._host, self._db, self._socket_connect_timeout, self._socket_timeout)
      if self._redis_server != None:
        return self._redis_server.hget(name, key)
    return None

  def publish(self, channel, message):
    if self._redis_server != None:
      self._redis_server.publish(channel, message)
      return True
    else:
      connect(self._host, self._db, self._socket_connect_timeout, self._socket_timeout)
      if self._redis_server != None:
        self._redis_server.publish(channel, message)
        return True
    return False
