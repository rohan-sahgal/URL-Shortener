#!/usr/bin/python3
# https://pypi.org/project/redis/
import redis
from cassandra_client import Cassandra_Client

redis_server = redis.Redis(host='redis', db=0, socket_connect_timeout=2, socket_timeout=2)
cassandra_server = Cassandra_Client(['172.17.0.1'], 'urlshortner')

r_sub = redis_server.pubsub()
r_sub.subscribe('urls_channel')
while (True):
  try:
    message = r_sub.get_message()
  except Exception as e:
    continue
  if (message):
    if (message['data'] == b'update'):
      short_long = redis_server.lpop('urls_list')
      if short_long:
        short_long = short_long.decode('utf-8').split(':::')
        try:
          cassandra_server.insert(short_long[0], short_long[1])
        except Exception as e:
          redis_server.lpush('urls_list', '{}:::{}'.format(short_long[0], short_long[1]))
          redis_server.publish('urls_channel', 'update')
