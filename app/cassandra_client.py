from cassandra.cluster import Cluster

insert_statement = """
UPDATE urls SET long_resource=%s WHERE short_resource=%s;
"""
select_statement = """
SELECT long_resource FROM urls WHERE short_resource=%s;
"""


class Cassandra_Client:
  def __init__(self, hosts, keyspace):
    self._hosts = hosts
    self._keyspace = keyspace
    self.connect(hosts, keyspace)
  
  def connect(self, hosts, keyspace):
    cluster = Cluster(hosts)
    self._session = cluster.connect(keyspace)

  def insert(self, short_resource, long_resource):
    if self._session == None:
      self.connect(self._hosts, self._keyspace)
    self._session.execute(insert_statement, (long_resource, short_resource))

  def get(self, short_resource):
    if self._session == None:
      self.connect(self._hosts, self._keyspace)
    rows = self._session.execute(select_statement, (short_resource, ))
    if rows:
      return rows[0].long_resource
    return None
