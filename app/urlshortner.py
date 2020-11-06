from flask import Flask
from flask import request
from flask import abort
from flask import render_template
from redis_client import Redis_Client
from cassandra_client import Cassandra_Client

app = Flask(__name__)
redis_server = Redis_Client('redis')
cassandra_server = Cassandra_Client(['10.11.12.17'], 'shortenerkeyspace')


@app.route('/', methods = ['PUT'])
def request_handler_put():
  short_resource = request.args.get('short')
  long_resource = request.args.get('long')
  if short_resource == None or long_resource == None or len(request.args) != 2:
    abort(400)
  cassandra_server.insert(short_resource, long_resource)
  return render_template('./redirect_recorded.html')

@app.route('/<short_resource>', methods = ['GET'])
def request_handler_get(short_resource):
  long_resource = redis_server.get('urls', short_resource)
  if long_resource != None and long_resource != '':
    return redirect(long_resource, code=307)
  long_resource = cassandra_server.get(short_resource)
  if long_resource != None and long_resource != '':
    redis_server.insert('urls', short_resource, long_resource)
    return redirect(long_resource, code=307)
  abort(404)



if __name__ == '__main__':
  app.run()
