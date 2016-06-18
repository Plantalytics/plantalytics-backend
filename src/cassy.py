from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import tuple_factory


auth = PlainTextAuthProvider(username='', password='')
cluster = Cluster([''], auth_provider=auth)
session = cluster.connect('')


def get_env_data():
    """
    Obtains temperature, humidity, and leaf wetness dataself.
    """
    session.row_factory = tuple_factory
    rows = session.execute("SELECT * FROM  ")
    return rows[0]
