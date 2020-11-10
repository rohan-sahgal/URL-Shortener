import logging
from flask import Flask
from flask import request
from flask import abort
from flask import render_template
from flask import redirect
from redis_client import Redis_Client
from cassandra_client import Cassandra_Client

application = Flask(__name__)
redis_server = Redis_Client('redis')
cassandra_server = Cassandra_Client(['172.17.0.1'], 'urlshortner')


@application.route('/', methods = ['GET', 'PUT'])
def request_handler_insert():
  if request.method == 'GET':
    application.logger.error('ERROR 400: BAD REQUEST')
    abort(400)
  short_resource = request.args.get('short')
  long_resource = request.args.get('long')
  if not short_resource or not long_resource or len(request.args) != 2:
    application.logger.error('ERROR 400: BAD REQUEST')
    abort(400)
  application.logger.info('PUT - short: {short_resource} long: {long_resource}')
  long_resource_redis = redis_server.get('urls', short_resource)
  if long_resource_redis:
    redis_server.insert('urls', short_resource, long_resource)
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
  application.logger.info(f'GET - /{short_resource}')
  long_resource = redis_server.get('urls', short_resource)
  if long_resource:
    application.logger.info('REDIS PROCESSED')
    return redirect(long_resource, code=307)
  long_resource = cassandra_server.get(short_resource)
  if long_resource:
    application.logger.info('CASSANDRA PROCESSED')
    redis_server.insert('urls', short_resource, long_resource)
    return redirect(long_resource, code=307)
  application.logger.error('ERROR 404: NOT FOUND')
  abort(404)


if __name__ != '__main__':
    # if we are not running directly, we set the loggers
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
  application.run(host='0.0.0.0', port=80)
