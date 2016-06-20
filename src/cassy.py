from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import named_tuple_factory

import yaml

config = yaml.safe_load(open("src/cassy_config.yml"))
auth = PlainTextAuthProvider(username=config['USERNAME'], password=config['PASSWORD'])
cluster = Cluster([config['HOST']], auth_provider=auth)
session = cluster.connect(config['KEYSPACE'])


def get_env_data(vineyard_id, variable_id):
    """
    Obtains temperature, humidity, and leaf wetness dataself.
    """

    # Dictionary to hold environmental variable id mappings
    env_variables = {
        '0': 'temperature',
        '1': 'humidity',
        '2': 'leafwetness',
    }

    variable = env_variables[variable_id]

    session.row_factory = named_tuple_factory
    rows = session.execute("SELECT " + variable + " FROM " + config['TABLE'] + " LIMIT 10")
    result = []

    if variable == 'temperature':
        for row in rows:
            result.append(row.temperature)
        return result
    elif variable == 'humidity':
        for row in rows:
            result.append(row.humidity)
        return result
    else:
        for row in rows:
            result.append(row.leafwetness)
        return result
