from flask import Flask
from flask import request
from flask import abort
from flask import render_template
from flask import redirect
from redis_client import Redis_Client
from cassandra_client import Cassandra_Client

application = Flask(__name__)
redis_server = Redis_Client('redis')
#redis_server_pubsub = Redis_Client('redis_pubsub')
cassandra_server = Cassandra_Client(['172.17.0.1'], 'urlshortner')


@application.route('/', methods = ['PUT'])
def request_handler_put():
  short_resource = request.args.get('short')
  long_resource = request.args.get('long')
  if not short_resource or not long_resource or len(request.args) != 2:
    abort(400)
  #redis_server.insert('urls', short_resource, long_resource)
  #redis_server_pubsub.insert_list('urls_list', short_resource, long_resource)
  #if not redis_server_pubsub.publish('urls_channel', 'update'):
  cassandra_server.insert(short_resource, long_resource)
  html = \
'''
<html>
      <body>
              <h1>Got It!</h1>
      </body>
</html>
'''
  return html

@application.route('/<short_resource>', methods = ['GET'])
def request_handler_get(short_resource):
  long_resource = redis_server.get('urls', short_resource)
  if long_resource:
    return redirect(long_resource, code=307)
  long_resource = cassandra_server.get(short_resource)
  if long_resource:
    redis_server.insert('urls', short_resource, long_resource)
    return redirect(long_resource, code=307)
  abort(404)


if __name__ == '__main__':
  application.run(host='0.0.0.0', port=80)
