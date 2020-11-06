from cassandra.cluster import Cluster

'''
profile = ExecutionProfile(
    load_balancing_policy=WhiteListRoundRobinPolicy(['127.0.0.1']),
    retry_policy=DowngradingConsistencyRetryPolicy(),
    consistency_level=ConsistencyLevel.LOCAL_QUORUM,
    serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
    request_timeout=15,
    row_factory=tuple_factory
)
# Can pass in execution profile 
cluster = Cluster(execution_profiles={EXEC_PROFILE_DEFAULT: profile})
'''

insert_statement = """
UPDATE resources SET long_resource=%s WHERE short_resource=%s;
"""
select_statement = """
SELECT long_resource FROM resources WHERE short_resource=%s;
"""

class Cassandra_Client:

  def __init__(hosts, keyspace):
    cluster = Cluster(hosts)
    self._session = cluster.connect(keyspace)

  def insert(short_resource, long_resource):
    self._session.execute(insert_statement, (short_resource, long_resource))

  def get(short_resource):
    rows = self._session.execute(select_statement, (short_resource))
    if len(rows) == 1:
      return rows.long_resource
    return None