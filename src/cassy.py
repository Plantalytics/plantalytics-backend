#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import os

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import named_tuple_factory

auth = PlainTextAuthProvider(username=os.environ.get('DB_USERNAME'),
                             password=os.environ.get('DB_PASSWORD'))
cluster = Cluster([os.environ.get('DB_HOST')], auth_provider=auth)
session = cluster.connect(os.environ.get('DB_KEYSPACE'))


def get_env_data(node_id, env_variable):
    """
    Obtains temperature, humidity, and leaf wetness dataself.
    """
    node = str(node_id)
    session.row_factory = named_tuple_factory
    rows = session.execute("SELECT " + env_variable
                           + " FROM " + os.environ.get('DB_ENV_TABLE')
                           + " WHERE nodeid = " + node + " LIMIT 1")

    # Exctract requested environmental variable.
    if env_variable == 'temperature':
        return rows[0].temperature
    elif env_variable == 'humidity':
        return rows[0].humidity
    else:
        return rows[0].leafwetness

def get_node_coordinates(vineyard_id):
    """
    Obtains the latitude and longitude coordinates for the nodes of a vineyard.
    """
    coordinates = []
    session.row_factory = named_tuple_factory
    rows = session.execute("SELECT nodeid, nodelocation"
                           + " FROM " + os.environ.get('DB_HW_TABLE')
                           + " WHERE vineid = " + vineyard_id)

    # Process node coordinates for requested vineyard.
    for node in rows:
        location = {}
        location["node_id"] = node.nodeid
        location["lat"] = node.nodelocation[0]
        location["lon"] = node.nodelocation[1]
        coordinates.append(location)
    return coordinates

def get_user_password(username):
    """
    Obtains password for the requested user.
    """
    session.row_factory = named_tuple_factory
    try:
        rows = session.execute('SELECT password'
                                + ' FROM ' + os.environ.get('DB_USER_TABLE')
                                + ' WHERE username = \''+ username + '\';')
        if not rows:
            raise Exception('Invlaid Username')
        else:
            return rows[0].password
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))
