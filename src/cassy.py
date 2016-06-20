from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import tuple_factory

import yaml

config = yaml.safe_load(open("src/cassy_config.yml"))
auth = PlainTextAuthProvider(username=config['USERNAME'], password=config['PASSWORD'])
cluster = Cluster([config['HOST']], auth_provider=auth)
session = cluster.connect(config['KEYSPACE'])


def get_env_data(vineyard_id, variable_id):
    """
    Obtains temperature, humidity, and leaf wetness dataself.
    """
    session.row_factory = tuple_factory
    result = session.execute("SELECT * FROM " + config['TABLE'] + " LIMIT 1")
    return result
