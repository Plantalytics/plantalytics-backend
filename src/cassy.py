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
    Obtains temperature, humidity, or leaf wetness dataset for a
    supplied node id and environmental variable.
    """

    supported_env_variables = [
        'leafwetness',
        'humidity',
        'temperature',
    ]
    if env_variable not in supported_env_variables:
        raise PlantalyticsDataException(ENV_DATA_INVALID)

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_ENV_TABLE'))
    parameters = {
        'nodeid': int(node_id),
    }
    query = (
        'SELECT {} FROM {} WHERE nodeid=? LIMIT 1;'
    )
    prepared_statement = session.prepare(
        query.format(str(env_variable), str(table))
    )

    try:
        rows = session.execute(
            prepared_statement,
            parameters
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
                # Shouldn't reach this point, but here for completeness
                raise PlantalyticsDataException(ENV_DATA_UNKNOWN)
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def store_env_data(env_data):
    """
    Inserts environmental data, received from a hub, into the database.
    """

    table = os.environ.get('DB_ENV_TABLE')
    query = (
        'INSERT INTO {} (nodeid, batchsent, datasent, hubid, '
        'humidity, leafwetness, temperature, vineid) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )
    batch_statement = BatchStatement()

    try:
        for data_point in env_data['hub_data']:
            data = (
                data_point['node_id'],
                env_data['batch_sent'],
                data_point['data_sent'],
                env_data['hub_id'],
                data_point['humidity'],
                data_point['leafwetness'],
                data_point['temperature'],
                env_data['vine_id']
            )
            batch_statement.add(
                prepared_statement,
                data
            )
        session.execute(batch_statement)
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def get_vineyard_coordinates(vineyard_id):
    """
    Obtains the coordinates for center point and boundary points of a vineyard
    matching the supplied vineyard id.
    """

    session.row_factory = named_tuple_factory
    table = os.environ.get('DB_VINE_TABLE')
    query = (
        'SELECT boundaries, center FROM {} WHERE vineid=?;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        if vineyard_id == '':
            raise PlantalyticsVineyardException(VINEYARD_NO_ID)
        # Ensures vineyard_id is integer
        vineyard_id = int(vineyard_id)
        parameters = {
            'vineid': vineyard_id,
        }
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            raise PlantalyticsVineyardException(VINEYARD_ID_NOT_FOUND)

        coordinates = []
        boundary_points = []

        center_point = {
            'lat': rows[0].center[0],
            'lon': rows[0].center[1],
        }
        coordinates.append(center_point)

        for point in rows[0].boundaries:
            boundary_point = {
                'lat': point[0],
                'lon': point[1],
            }
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
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def get_node_coordinates(vineyard_id):
    """
    Obtains the latitude and longitude coordinates for the nodes of a vineyard
    matching the supplied vineyard id.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_HW_TABLE'))
    query = (
            'SELECT nodeid, nodelocation FROM {} WHERE vineid=?;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        if vineyard_id == '':
            raise PlantalyticsVineyardException(VINEYARD_NO_ID)
        # Confirms vineyard_id is an integer
        # Raises ValueError if not
        vineyard_id = int(vineyard_id)
        parameters = {
            'vineid': vineyard_id,
        }
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            raise PlantalyticsVineyardException(VINEYARD_ID_NOT_FOUND)

        # Process node coordinates for requested vineyard.
        coordinates = []
        for node in rows:
            location = {
                'node_id': node.nodeid,
                'lat': node.nodelocation[0],
                'lon': node.nodelocation[1],
            }
            coordinates.append(location)
        return coordinates
    except PlantalyticsException as e:
        raise e
    except ValueError as e:
        raise PlantalyticsVineyardException(VINEYARD_BAD_ID)
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def get_user_password(username):
    """
    Obtains password for the requested user.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
    }
    query = (
        'SELECT password FROM {} WHERE username=?;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        if username == '':
            raise PlantalyticsLoginException(LOGIN_ERROR)
        rows = session.execute(
            prepared_statement,
            parameters
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
        raise Exception('Transaction Error Occurred: {}'.format(str(e)))


def get_user_email(username):
    """
    Obtains email for the requested user.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
    }
    query = (
        'SELECT email FROM {} WHERE username=?'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        if username == '':
            raise PlantalyticsEmailException(EMAIL_ERROR)
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            raise PlantalyticsEmailException(EMAIL_ERROR)
        else:
            return rows[0].email
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def get_user_auth_token(username, password):
    """
    Obtains session authentication token for the requested user.
    Assumes the username and password have already been validated
    prior to calling this function.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
        'password': password,
    }
    query = (
        'SELECT securitytoken FROM {} WHERE username=? AND password=?;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            raise PlantalyticsAuthException(AUTH_NOT_FOUND)
        else:
            return rows[0].securitytoken
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


def set_user_auth_token(username, password, auth_token):
    """
    Stores the session authentication token for the requested user.
    Assumes username and password have already been validated
    prior to calling this function.
    """

    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
        'password': password,
        'securitytoken': auth_token,
    }
    query = (
        'INSERT INTO {} (username, password, securitytoken) VALUES(?, ?, ?);'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    if auth_token == '':
        raise PlantalyticsAuthException(AUTH_NO_TOKEN)
    try:
        session.execute(
            prepared_statement,
            parameters
        )
        return True
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def verify_auth_token(auth_token):
    """
    Verifies session authentication token exists in the database.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'securitytoken': auth_token,
    }
    query = (
        'SELECT username FROM {} WHERE securitytoken=? ALLOW FILTERING;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            raise PlantalyticsAuthException(AUTH_NOT_FOUND)
        return rows[0].username
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def change_user_password(username, new_password, old_password):
    """
    Changes current password of the supplied username
    to the supplied password.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
    }
    query = (
        'SELECT * FROM {} WHERE username=?;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        # Verify that the supplied username exists
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            raise PlantalyticsAuthException(RESET_ERROR_USERNAME)

        # Insert new row with new password.
        new_row_values = {
            'username': rows[0].username,
            'password': new_password,
            'email': rows[0].email,
            'securitytoken': rows[0].securitytoken,
            'subenddate': rows[0].subenddate,
            'userid': rows[0].userid,
            'vineyards': rows[0].vineyards,
        }
        query = (
            'INSERT INTO {} '
            '(username, password, email, securitytoken, '
            'subenddate, userid, vineyards) '
            'VALUES(?, ?, ?, ?, ?, ?, ?);'
        )
        prepared_statement = session.prepare(
            query.format(table)
        )

        session.execute(
            prepared_statement,
            new_row_values
        )

        # Delete old row with old password.
        old_row_values = {
            'username': username,
            'password': old_password,
        }
        query = (
            'DELETE FROM {} WHERE username=? AND password=?;'
        )
        prepared_statement = session.prepare(
            query.format(table)
        )

        session.execute(
            prepared_statement,
            old_row_values
        )
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.foramt(str(e)))
