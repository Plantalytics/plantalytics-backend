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
            raise PlantalyticsEmailException(EMAIL_RESET_ERROR)
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            raise PlantalyticsEmailException(EMAIL_RESET_ERROR)
        else:
            return rows[0].email
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def get_authorized_vineyards(username):
    """
    Obtains authorized vineyard ids for requested user.
    """

    values = {'username': username}
    vineyards_stmt_get = session.prepare(
        'SELECT vineyards'
        + ' FROM ' + os.environ.get('DB_USER_TABLE')
        + ' WHERE username=?'
    )
    bound = vineyards_stmt_get.bind(values)
    session.row_factory = named_tuple_factory

    try:
        if username == '':
            raise PlantalyticsEmailException(EMAIL_ERROR)
        rows = session.execute(bound)

        if not rows:
            raise PlantalyticsLoginException(LOGIN_NO_VINEYARDS)
        else:
            # Loop through vineyards and grab vineyard names
            vineyard_ids = rows[0].vineyards
            vineyard_object_array = []

            # Assemble array of vineyard id/name combinations
            for vine in vineyard_ids:
                # Perform query for vineyard name
                values = {'vineid': vine}
                vineyard_names_stmt_get = session.prepare(
                    'SELECT vinename'
                    + ' FROM ' + os.environ.get('DB_VINE_TABLE')
                    + ' WHERE vineid=?'
                )
                bound = vineyard_names_stmt_get.bind(values)
                session.row_factory = named_tuple_factory
                name_rows = session.execute(bound)

                cur_vineyard_object = {
                    'vineyard_id': vine,
                    'vineyard_name': name_rows[0].vinename
                }
                vineyard_object_array.append(cur_vineyard_object)

            # Return completed object.
            return vineyard_object_array
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: ' + str(e))


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
            'admin': rows[0].admin,
            'email': rows[0].email,
            'enable': rows[0].enable,
            'securitytoken': rows[0].securitytoken,
            'subenddate': rows[0].subenddate,
            'userid': rows[0].userid,
            'vineyards': rows[0].vineyards,
        }
        query = (
            'INSERT INTO {} '
            '(username, password, admin, email, enable, securitytoken, '
            'subenddate, userid, vineyards) '
            'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);'
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
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def change_user_email(username, new_email):
    """
    Changes email address of the supplied username
    to the supplied email
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
        'email': new_email,
    }
    query = (
        'UPDATE {} SET email=? WHERE username=? AND password=?;'
    )

    try:
        password = get_user_password(username)
        parameters['password'] = password
        prepared_statement = session.prepare(
            query.format(table)
        )
        session.execute(
            prepared_statement,
            parameters
        )
        return True
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def verify_authenticated_admin(auth_token):
    """
    Verifies if supplied username is an admin and is authenticated.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'securitytoken': auth_token,
    }
    query = (
        'SELECT admin FROM {} WHERE securitytoken=? ALLOW FILTERING;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if (not rows or rows[0].admin is False):
            return False
        if (rows[0].admin is True):
            return True
        return False
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def get_user_info(username):
    """
    Obtains email, user id, and vineyard ids for submitted user.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
    }
    query = (
        'SELECT admin, email, enable, subenddate, userid, vineyards '
        'FROM {} WHERE username=?;'
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
            raise PlantalyticsAuthException(USER_INVALID)
        user_info = {
            'is_admin': rows[0].admin,
            'email': rows[0].email,
            'is_enabled': rows[0].enable,
            'sub_end_date': rows[0].subenddate,
            'user_id': rows[0].userid,
            'vineyards': rows[0].vineyards,
        }
        return user_info
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def create_new_user(new_user_info):
    """
    Creates new user in DB using the submitted info.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
            'username': new_user_info.get('username', ''),
            'password': new_user_info.get('password', ''),
            'email': new_user_info.get('email', ''),
            'admin': new_user_info.get('admin', ''),
            'enable': new_user_info.get('enable', ''),
            'subenddate': new_user_info.get('subenddate', ''),
            'userid': int(new_user_info.get('userid', '')),
            'vineyards': new_user_info.get('vineyards', ''),
    }
    query = (
        'INSERT INTO {} (username, password, admin, email, enable, '
        'subenddate, userid, vineyards) '
        'VALUES(?, ?, ?, ?, ?, ?, ?, ?);'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        session.execute(
            prepared_statement,
            parameters
        )
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def update_user_subscription(username, sub_end_date):
    """
    Updates the subscription end date for the supplied user.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
        'subenddate': sub_end_date,
    }
    query = (
        'UPDATE {} SET subenddate=? WHERE username=? AND password=?;'
    )

    try:
        password = get_user_password(username)
        if not password:
            raise PlantalyticsAuthException(USER_INVALID)
        parameters['password'] = password
        prepared_statement = session.prepare(
            query.format(table)
        )
        session.execute(
            prepared_statement,
            parameters
        )
        return True
    # Known exception
    except PlantalyticsLoginException as e:
            raise PlantalyticsAuthException(USER_INVALID)
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def disable_user(username):
    """
    Disables user in DB for submitted username.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': username,
        'enable': False,
    }
    query = (
        'UPDATE {} SET enable=? WHERE username=? AND password=?;'
    )

    try:
        password = get_user_password(username)
        if not password:
            raise PlantalyticsAuthException(USER_INVALID)
        parameters['password'] = password
        prepared_statement = session.prepare(
            query.format(table)
        )
        session.execute(
            prepared_statement,
            parameters
        )
        return True
    # Known exception
    except PlantalyticsLoginException as e:
            raise PlantalyticsAuthException(USER_INVALID)
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def edit_user(user_edit_info):
    """
    Edits user info in DB using submitted info.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'username': user_edit_info.get('username', ''),
    }
    query = (
        'SELECT * FROM {} WHERE username=?;'
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
            raise PlantalyticsAuthException(USER_INVALID)
        old_row = {
            'username': rows[0].username,
            'password': rows[0].password,
        }

        edit_row = {
            'username': rows[0].username,
            'password': rows[0].password,
            'admin': rows[0].admin,
            'email': rows[0].email,
            'enable': rows[0].enable,
            'securitytoken': rows[0].securitytoken,
            'subenddate': rows[0].subenddate,
            'userid': rows[0].userid,
            'vineyards': rows[0].vineyards,
        }

        for key in user_edit_info:
            if (user_edit_info.get(key, '') != ''):
                edit_row[key] = user_edit_info.get(key, '')

        query = (
            'INSERT INTO {} '
            '(username, password, admin, email, enable, '
            'securitytoken, subenddate, userid, vineyards) '
            'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);'
        )
        prepared_statement = session.prepare(
            query.format(table)
        )
        session.execute(
            prepared_statement,
            edit_row
        )
        new_password = edit_row.get('password', '')
        old_password = old_row.get('password', '')
        if (new_password != old_password):
            query = (
                'DELETE FROM {} WHERE username=? AND password=?;'
            )
            prepared_statement = session.prepare(
                query.format(table)
            )
            session.execute(
                prepared_statement,
                old_row
            )
        return True
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def edit_vineyard(edit_vineyard_info):
    """
    Edits vineyard info in DB using submitted info.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_VINE_TABLE'))
    parameters = {
        'vineid': int(edit_vineyard_info.get('vineyard_id', '')),
    }
    query = (
        'SELECT * FROM {} WHERE vineid=?;'
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
            raise PlantalyticsAuthException(VINEYARD_BAD_ID)
        old_row = {
            'vineid': rows[0].vineid,
        }

        edit_row = {
            'vineid': rows[0].vineid,
            'boundaries': rows[0].boundaries,
            'center': rows[0].center,
            'enable': rows[0].enable,
            'ownerlist': rows[0].ownerlist,
            'vinename': rows[0].vinename,
        }
        if (edit_vineyard_info.get('vineyard_id', '') != ''):
            edit_row['vineid'] = int(edit_vineyard_info.get('vineyard_id', ''))
        if (edit_vineyard_info.get('boundaries', '') != ''):
            boundaries = []
            for point in edit_vineyard_info.get('boundaries', ''):
                coordinate = (
                    float(point['lon']),
                    float(point['lat'])
                )
                boundaries.append(coordinate)
            edit_row['boundaries'] = boundaries
        if (edit_vineyard_info.get('center', '') != ''):
            center_point = edit_vineyard_info.get('center', '')
            center = (
                float(center_point['lon']),
                float(center_point['lat']),
            )
            edit_row['center'] = center
        if (edit_vineyard_info.get('enable', '') != ''):
            edit_row['enable'] = edit_vineyard_info.get('enable', '')
        if (edit_vineyard_info.get('owners', '') != ''):
            edit_row['ownerlist'] = edit_vineyard_info.get('owners', '')
        if (edit_vineyard_info.get('name', '') != ''):
            edit_row['vinename'] = edit_vineyard_info.get('name', '')

        query = (
            'INSERT INTO {} '
            '(vineid, boundaries, center, enable, ownerlist, vinename) '
            'VALUES(?, ?, ?, ?, ?, ?);'
        )
        prepared_statement = session.prepare(
            query.format(table)
        )
        session.execute(
            prepared_statement,
            edit_row
        )
        return True
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def create_new_vineyard(new_vineyard_info):
    """
    Creates new vineyard in DB using the submitted info.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_VINE_TABLE'))
    parameters = {
            'vineid': int(new_vineyard_info.get('vineyard_id', '')),
            'ownerlist': new_vineyard_info.get('owners', ''),
            'vinename': new_vineyard_info.get('name', ''),
            'enable': new_vineyard_info.get('enable', ''),
    }
    boundaries = []
    for point in new_vineyard_info.get('boundaries', ''):
        coordinate = (
            float(point['lon']),
            float(point['lat'])
        )
        boundaries.append(coordinate)
    center_point = new_vineyard_info.get('center', '')
    center = (
        float(center_point['lon']),
        float(center_point['lat']),
    )
    parameters['boundaries'] = boundaries
    parameters['center'] = center
    query = (
        'INSERT INTO {} '
        '(vineid, boundaries, center, enable, ownerlist, vinename) '
        'VALUES(?, ?, ?, ?, ?, ?);'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        session.execute(
            prepared_statement,
            parameters
        )
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def get_vineyard_users(vineyard_id):
    """
    Obtains the users of the supplied vineyard id.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    query = (
        'SELECT username FROM {} WHERE vineyards CONTAINS ' +
        str(vineyard_id) + ';'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        rows = session.execute(
            prepared_statement
        )
        if not rows:
            raise PlantalyticsAuthException(AUTH_NOT_FOUND)
        users = []
        for row in rows:
            users.append(row.username)
        return users
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def get_vineyard_info(vineyard_id):
    """
    Obtains the name, owners, and users of a vineyard
    matching the supplied vineyard id.
    """

    session.row_factory = named_tuple_factory
    table = os.environ.get('DB_VINE_TABLE')
    query = (
        'SELECT vinename, ownerlist, enable FROM {} WHERE vineid=?;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        if vineyard_id == '':
            raise PlantalyticsVineyardException(VINEYARD_NO_ID)
        # Ensures vineyard_id is integer
        vineyard_id = int(vineyard_id)
        if vineyard_id < 0:
            raise PlantalyticsVineyardException(VINEYARD_BAD_ID)
        parameters = {
            'vineid': vineyard_id,
        }
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            raise PlantalyticsVineyardException(VINEYARD_ID_NOT_FOUND)

        owners = []
        for owner in rows[0].ownerlist:
            owners.append(owner)
        users = get_vineyard_users(vineyard_id)
        vineyard_info = {
            'name': rows[0].vinename,
            'owners': owners,
            'users': users,
            'is_enable': rows[0].enable,
        }
        return vineyard_info
    # Known exception
    except PlantalyticsAuthException as e:
        raise PlantalyticsVineyardException(VINEYARD_ID_NOT_FOUND)
    except PlantalyticsException as e:
        raise e
    except ValueError as e:
        raise PlantalyticsVineyardException(VINEYARD_BAD_ID)
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def disable_vineyard(vineyard_id):
    """
    Disables vineyard in DB for submitted vineyard id.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_VINE_TABLE'))
    parameters = {
        'vineid': int(vineyard_id),
    }
    query = (
        'SELECT * FROM {} WHERE vineid=?;'
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
            raise PlantalyticsVineyardException(VINEYARD_BAD_ID)
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))

    parameters['enable'] = False
    query = (
        'UPDATE {} SET enable=? WHERE vineid=?;'
    )
    prepared_statement = session.prepare(
        query.format(table)
    )

    try:
        session.execute(
            prepared_statement,
            parameters
        )
        return True
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def check_username_exists(username):
    """
    Checks if submitted username exists in the database.
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
        rows = session.execute(
            prepared_statement,
            parameters
        )
        if not rows:
            return False
        return True
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def check_user_id_exists(user_id):
    """
    Checks if submitted user ID exists in the database.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_USER_TABLE'))
    parameters = {
        'userid': int(user_id),
    }
    query = (
        'SELECT * FROM {} WHERE userid=? ALLOW FILTERING;'
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
            return False
        return True
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))


def check_vineyard_id_exists(vineyard_id):
    """
    Checks if submitted vineyard ID exists in the database.
    """

    session.row_factory = named_tuple_factory
    table = str(os.environ.get('DB_VINE_TABLE'))
    parameters = {
        'vineid': int(vineyard_id),
    }
    query = (
        'SELECT * FROM {} WHERE vineid=?;'
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
            return False
        return True
    # Known exception
    except PlantalyticsException as e:
        raise e
    # Unknown exception
    except Exception as e:
        raise Exception('Transaction Error Occurred: '.format(str(e)))
