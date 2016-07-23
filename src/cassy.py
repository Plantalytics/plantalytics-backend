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

auth = PlainTextAuthProvider(
            username=os.environ.get('DB_USERNAME'),
            password=os.environ.get('DB_PASSWORD')
)
cluster = Cluster(
            [os.environ.get('DB_HOST')],
            auth_provider=auth
)
session = cluster.connect(os.environ.get('DB_KEYSPACE'))

# Prepared statements

auth_stmt_get = session.prepare('SELECT securitytoken'
                                + ' FROM ' + os.environ.get('DB_USER_TABLE')
                                + ' WHERE username=? AND password=?;')
auth_stmt_set = session.prepare('INSERT INTO '
                                + os.environ.get('DB_USER_TABLE')
                                + ' (username, password, securitytoken)'
                                + ' VALUES(?, ?, ?);')


def get_env_data(node_id, env_variable):
    """
    Obtains temperature, humidity, and leaf wetness dataself.
    """

    node = str(node_id)
    session.row_factory = named_tuple_factory

    try:
        rows = session.execute(
            'SELECT ' + env_variable
            + ' FROM ' + os.environ.get('DB_ENV_TABLE')
            + ' WHERE nodeid = ' + node + ' LIMIT 1;'
        )

        if not rows:
            raise Exception('Invalid Environmental Variable or Node ID')
        else:
            # Exctract requested environmental variable.
            if env_variable == 'temperature':
                return rows[0].temperature
            elif env_variable == 'humidity':
                return rows[0].humidity
            else:
                return rows[0].leafwetness
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def get_vineyard_coordinates(vineyard_id):
    """
    Obtains the coordinates for center point and boundary of a vineyard.
    """

    coordinates = []
    session.row_factory = named_tuple_factory

    try:
        rows = session.execute(
            'SELECT boundaries, center'
            + ' FROM ' + os.environ.get('DB_VINE_TABLE')
            + ' WHERE vineid = ' + vineyard_id + ';'
        )

        if not rows:
            raise Exception('Invalid Vineyard ID')
        else:
            center_point = {}
            boundary_points = []

            center_point['lat'] = rows[0].center[0]
            center_point['lon'] = rows[0].center[1]
            coordinates.append(center_point)

            for point in rows[0].boundaries:
                boundary_point = {}
                boundary_point['lat'] = point[0]
                boundary_point['lon'] = point[1]
                boundary_points.append(boundary_point)

            coordinates.append(boundary_points)
            return coordinates
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def get_node_coordinates(vineyard_id):
    """
    Obtains the latitude and longitude coordinates for the nodes of a vineyard.
    """

    coordinates = []
    session.row_factory = named_tuple_factory

    try:
        rows = session.execute(
            'SELECT nodeid, nodelocation'
            + ' FROM ' + os.environ.get('DB_HW_TABLE')
            + ' WHERE vineid = ' + vineyard_id + ';'
        )

        if not rows:
            raise Exception('Invalid Vineyard ID')
        else:
            # Process node coordinates for requested vineyard.
            for node in rows:
                location = {}
                location['node_id'] = node.nodeid
                location['lat'] = node.nodelocation[0]
                location['lon'] = node.nodelocation[1]
                coordinates.append(location)
            return coordinates
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def get_user_password(username):
    """
    Obtains password for the requested user.
    """

    session.row_factory = named_tuple_factory

    try:
        rows = session.execute(
            'SELECT password'
            + ' FROM ' + os.environ.get('DB_USER_TABLE')
            + ' WHERE username = \'' + username + '\';'
        )

        if not rows:
            raise Exception('Invalid Username')
        else:
            return rows[0].password
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def get_user_auth_token(username, password):
    """
    Obtains session authentication token for the requested user.
    """

    bound = auth_stmt_get.bind(username, password)
    session.row_factory = named_tuple_factory

    try:
        rows = session.execute(bound)

        if not rows:
            raise Exception('Invalid Username and/or Password')
        else:
            return rows[0].securitytoken
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def set_user_auth_token(username, password, securitytoken):
    """
    Stores the session authentication token for the requested user.
    """

    bound = auth_stmt_set.bind(username, password, securitytoken)

    try:
        session.execute(bound)

    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))
