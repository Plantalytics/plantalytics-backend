#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import os

from common.exceptions import *
from common.errors import *
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import named_tuple_factory, BatchStatement


auth = PlainTextAuthProvider(
            username=os.environ.get('DB_USERNAME'),
            password=os.environ.get('DB_PASSWORD')
)
cluster = Cluster(
            [os.environ.get('DB_HOST')],
            auth_provider=auth
)
session = cluster.connect(os.environ.get('DB_KEYSPACE'))


def get_env_data(node_id, env_variable):
    """
    Obtains temperature, humidity, and leaf wetness dataself.
    """

    node = str(node_id)
    session.row_factory = named_tuple_factory

    if env_variable not in ['leafwetness', 'humidity', 'temperature']:
        raise PlantalyticsDataException(ENV_DATA_INVALID)

    try:
        rows = session.execute(
            'SELECT ' + env_variable
            + ' FROM ' + os.environ.get('DB_ENV_TABLE')
            + ' WHERE nodeid = ' + node + ' LIMIT 1;'
        )

        if not rows:
            raise PlantalyticsDataException(ENV_DATA_NOT_FOUND)
        else:
            # Extract requested environmental variable.
            if env_variable == 'temperature':
                return rows[0].temperature
            elif env_variable == 'humidity':
                return rows[0].humidity
            elif env_variable == 'leafwetness':
                return rows[0].leafwetness
            else:
                # Shouldn't get to this point, but here for completeness
                raise PlantalyticsDataException(ENV_DATA_UNKNOWN)
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def post_env_data(env_data):
    """
    Inserts data from hub into database.
    """

    insert_env_data = session.prepare(
        'INSERT INTO ' + os.environ.get('DB_ENV_TABLE') +
        ' (nodeid, batchsent, datasent, hubid,' +
        ' humidity, leafwetness, temperature, vineid)' +
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    )
    batch = BatchStatement()

    try:
        for data_point in env_data['hub_data']:
            batch.add(
                insert_env_data,
                (
                    data_point['node_id'],
                    env_data['batch_sent'],
                    data_point['data_sent'],
                    env_data['hub_id'],
                    data_point['humidity'],
                    data_point['leafwetness'],
                    data_point['temperature'],
                    env_data['vine_id']
                )
            )
        session.execute(batch)
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def get_vineyard_coordinates(vineyard_id):
    """
    Obtains the coordinates for center point and boundary of a vineyard.
    """

    coordinates = []
    session.row_factory = named_tuple_factory

    try:
        if vineyard_id == '':
            raise PlantalyticsVineyardException(VINEYARD_NO_ID)
        # Ensures vineyard_id is integer
        int(vineyard_id)
        rows = session.execute(
            'SELECT boundaries, center'
            + ' FROM ' + os.environ.get('DB_VINE_TABLE')
            + ' WHERE vineid = ' + vineyard_id + ';'
        )

        if not rows:
            raise PlantalyticsVineyardException(VINEYARD_ID_NOT_FOUND)
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
    # Known exception
    except PlantalyticsException as e:
        raise e
    except ValueError as e:
        raise PlantalyticsVineyardException(VINEYARD_BAD_ID)
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def get_node_coordinates(vineyard_id):
    """
    Obtains the latitude and longitude coordinates for the nodes of a vineyard.
    """
    coordinates = []
    session.row_factory = named_tuple_factory

    try:
        if vineyard_id == '':
            raise PlantalyticsVineyardException(VINEYARD_NO_ID)
        # Confirms vineyard_id is a string representation of an integer
        # Raises ValueError if not
        int(vineyard_id)
        rows = session.execute(
            'SELECT nodeid, nodelocation'
            + ' FROM ' + os.environ.get('DB_HW_TABLE')
            + ' WHERE vineid = ' + vineyard_id + ';'
        )
        if not rows:
            raise PlantalyticsVineyardException(VINEYARD_ID_NOT_FOUND)
        else:
            # Process node coordinates for requested vineyard.
            for node in rows:
                location = {}
                location['node_id'] = node.nodeid
                location['lat'] = node.nodelocation[0]
                location['lon'] = node.nodelocation[1]
                coordinates.append(location)
            return coordinates
    except PlantalyticsException as e:
        raise e
    except ValueError as e:
        raise PlantalyticsVineyardException(VINEYARD_BAD_ID)
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def get_user_password(username):
    """
    Obtains password for the requested user.
    """

    session.row_factory = named_tuple_factory

    try:
        if username == '':
            raise PlantalyticsLoginException(LOGIN_ERROR)
        rows = session.execute(
            'SELECT password'
            + ' FROM ' + os.environ.get('DB_USER_TABLE')
            + ' WHERE username = \'' + username + '\';'
        )

        if not rows:
            raise PlantalyticsLoginException(LOGIN_ERROR)
        else:
            return rows[0].password
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))

def get_user_email(username):
    """
    Obtains email for the requested user.
    """

    values = {}
    values['username'] = username
    auth_stmt_get = session.prepare(
        'SELECT email'
        + ' FROM ' + os.environ.get('DB_USER_TABLE')
        + ' WHERE username=?'
    )
    bound = auth_stmt_get.bind(values)
    session.row_factory = named_tuple_factory

    try:
        if username == '':
            raise PlantalyticsEmailException(EMAIL_ERROR)
        rows = session.execute(bound)

        if not rows:
            raise PlantalyticsEmailException(EMAIL_ERROR)
        else:
            return rows[0].email
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def get_user_auth_token(username, password):
    """
    Obtains session authentication token for the requested user.
    Assuming the username and password have already been validated prior to calling this function.
    """

    values = {}
    values['username'] = username
    values['password'] = password
    auth_stmt_get = session.prepare(
        'SELECT securitytoken'
        + ' FROM ' + os.environ.get('DB_USER_TABLE')
        + ' WHERE username=? AND password=?;'
    )
    bound = auth_stmt_get.bind(values)
    session.row_factory = named_tuple_factory

    try:
        rows = session.execute(bound)

        if not rows:
            raise PlantalyticsAuthException(AUTH_NOT_FOUND)
        else:
            return rows[0].securitytoken
    except PlantalyticsException as e:
        raise e
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def set_user_auth_token(username, password, auth_token):
    """
    Stores the session authentication token for the requested user.
    Assuming username and password have already been validated prior to calling this function.
    """

    values = {}
    values['username'] = username
    values['password'] = password
    values['securitytoken'] = auth_token
    auth_stmt_set = session.prepare(
        'INSERT INTO '
        + os.environ.get('DB_USER_TABLE')
        + ' (username, password, securitytoken)'
        + ' VALUES(?, ?, ?);'
    )
    bound = auth_stmt_set.bind(values)

    if auth_token == '':
        raise PlantalyticsAuthException(AUTH_NO_TOKEN)
    try:
        session.execute(bound)
        return True

    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))

def verify_auth_token(auth_token):
    """
    Verifies session authentication token.
    """
    values = {}
    values['securitytoken'] = auth_token

    auth_stmt_get = session.prepare(
        'SELECT username'
        + ' FROM ' + os.environ.get('DB_USER_TABLE')
        + ' WHERE securitytoken=?'
        + ' ALLOW FILTERING;'
    )
    bound = auth_stmt_get.bind(values)
    session.row_factory = named_tuple_factory

    try:
        rows = session.execute(bound)
        if not rows:
            raise PlantalyticsAuthException(AUTH_NOT_FOUND)

        return rows[0].username

    except PlantalyticsException as e:
        raise e
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def change_user_password(username, new_password, old_password):
    """
    Changes current password of the supplied username
    to the supplied password.
    """
    values = {}
    values['username'] = username

    auth_stmt_get = session.prepare(
        'SELECT *'
        + ' FROM ' + os.environ.get('DB_USER_TABLE')
        + ' WHERE username=?;'
    )
    bound = auth_stmt_get.bind(values)
    session.row_factory = named_tuple_factory

    try:
        rows = session.execute(bound)
        if not rows:
            raise PlantalyticsAuthException(RESET_ERROR_USERNAME)

        # Insert new row with new password.
        new_values = {}
        new_values['username'] = rows[0].username
        new_values['password'] = new_password
        new_values['email'] = rows[0].email
        new_values['securitytoken'] = rows[0].securitytoken
        new_values['subenddate'] = rows[0].subenddate
        new_values['userid'] = rows[0].userid
        new_values['vineyards'] = rows[0].vineyards
        auth_stmt_set = session.prepare(
            'INSERT INTO '
            + os.environ.get('DB_USER_TABLE')
            + ' (username, password, email, securitytoken, subenddate, userid, vineyards)'
            + ' VALUES(?, ?, ?, ?, ?, ?, ?);'
        )
        new_bound = auth_stmt_set.bind(new_values)
        session.execute(new_bound)

        # Delete old row with old password.
        old_values = {}
        old_values['username'] = username
        old_values['password'] = old_password
        auth_stmt_set = session.prepare(
            'DELETE FROM '
            + os.environ.get('DB_USER_TABLE')
            + ' WHERE username=? AND password=?;'
        )
        old_bound = auth_stmt_set.bind(old_values)
        session.execute(old_bound)

    except PlantalyticsException as e:
        raise e
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))
