import object_utils

import os
import math
import logging
log = logging.getLogger(__file__)


def add_schema(schema, data_classes=[]):
    """
    will add the schema meta data to the __table__ element in the data access classes
    """
    if schema and len(schema) > 0 and data_classes and len(data_classes) > 0:
        for c in data_classes:
            if c and hasattr(c, '__table__'):
                c.__table__.schema = schema


def check_create_db(db_url, is_geospatial=False):
    """ generic check a database ... and create it if it doesn't exist
        @TODO: add other database supports beyond postgres
    """
    #import pdb; pdb.set_trace()
    ret_val = True
    if 'postgres' in db_url:
        db_name = database_name_from_url(db_url)
        db_user = username_from_url(db_url, def_val=os.getenv('USERNAME'))
        ret_val = postgres_check_create_db(db_name, db_user, is_geospatial)

    return ret_val


def make_url(db_url, def_val=None):
    """ diaper wrapper around sqlalchemy's make_url
    """
    ret_val = def_val
    try:
        from sqlalchemy.engine.url import make_url as sa_make_url
        url = sa_make_url(db_url)
        log.debug("{} {} {} {} {}".format(url.username, url.password, url.host, url.port, url.database))
        ret_val = url
    except Exception as e:
        log.error("DB URL {} PARSE ERROR : {}".format(db_url, e))
    return ret_val


def database_name_from_url(db_url, def_val=None):
    ret_val = def_val
    u = make_url(db_url)
    if u and u.database:
        ret_val = u.database
    return ret_val


def username_from_url(db_url, def_val=None):
    ret_val = def_val
    u = make_url(db_url)
    if u and u.username:
        ret_val = u.username
    return ret_val


def db_conn(url):
    """  create a generic scoped session to a database as defined by the param url
         via sqlalchemy.  This routine meant as a quick way to grab a session / engine
         @param url: sqlite:///gtfs.db or postgresql+psycopg2://postgres@localhost:5432/transit
         @return: session, engine 
    """
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker
    session = scoped_session(sessionmaker())

    # create the engine
    from sqlalchemy import create_engine
    engine = create_engine(url)
    session.configure(bind=engine)

    return session, engine


def gtfsdb_conn(kwargs):
    from gtfsdb import Database
    db = Database(**kwargs)
    return db


def gtfsdb_conn_parts(db_url, schema=None, is_geospatial=False):
    """ make Database() from individual url/schemal/geometry flag """
    kwargs = gtfsdb_param(db_url, schema, is_geospatial)
    return gtfsdb_conn(kwargs)


def gtfsdb_conn_from_config(config):
    u, s, g = db_params_from_config(config)
    return gtfsdb_conn_parts(u, s, g)


def gtfsdb_param(db_url, schema=None, is_geospatial=False):
    """
    return kv pair for gtfsdb from parts
    """
    kwargs = dict(
        url=db_url,
        schema=schema,
        is_geospatial=is_geospatial
    )
    return kwargs


def gtfsdb_param_from_config(config):
    """ simple utility to pull url, schema and is/not geospatial from config .ini file and format into gtfsdb kv dict"""
    u, s, g = db_params_from_config(config)
    ret_val = gtfsdb_param(u, s, g)
    return ret_val


def db_params_from_config(config):
    """ simple utility to pull url, schema and is/not geospatial from config .ini file """
    u = object_utils.safe_dict_val(config, 'sqlalchemy.url')
    s = object_utils.safe_dict_val(config, 'sqlalchemy.schema')
    g = object_utils.safe_dict_val(config, 'sqlalchemy.is_geospatial', False)
    return u, s, g


def closest_stops_tuple_to_dict(tup):
    ret_val = {
        'stop_id'    : tup[1],
        'stop_name'  : tup[0],
        'stop_lat'   : tup[2],
        'stop_lon'   : tup[3],
        'dist_miles' : tup[4]
    }
    return ret_val


def add_math_to_sqllite(conn, conn_record):
    """ This method is called for each new SQLAlchemy database connection. I'm using it as a connection decorator to
        add math routines to a sqllite database

        @note: check out the call to (above): event.listen(self.engine, 'connect', Database.connection)
        @see:  http://docs.sqlalchemy.org/en/rel_0_8/core/events.html#sqlalchemy.events.PoolEvents
    """
    if 'sqlite' in type(conn).__module__:        
        print("in method that adds math to sqllite")
        conn.create_function("sin",     1, math.sin)
        conn.create_function("cos",     1, math.cos)
        conn.create_function("acos",    1, math.acos)
        conn.create_function("sqrt",    1, math.sqrt)
        conn.create_function("pow",     2, math.pow)
        conn.create_function("radians", 1, math.radians)


def decorate_engine(engine, method=add_math_to_sqllite):
    """ for
    """
    from sqlalchemy import event
    event.listen(engine, 'connect', method)


def sqlite_nearest_query(schema=None, table='stops'):
    """
        http://www.plumislandmedia.net/mysql/haversine-mysql-nearest-loc/

        SELECT stop_name, stop_code, stop_lat, stop_lon, 
               (3963.17 * ACOS(COS(RADIANS(45.587)) 
                 * COS(RADIANS(stop_lat)) 
                 * COS(RADIANS(-122.593) - RADIANS(stop_lon)) 
                 + SIN(RADIANS(45.587)) 
                 * SIN(RADIANS(stop_lat)))) 
                 AS miles_away
        FROM ott.stops
        ORDER BY miles_away
        LIMIT 15
    """
    if schema:
        table = "{0}.{1}".format(schema, table)

    clause = ( "SELECT stop_code, stop_name, stop_lat, stop_lon, "
               "(3963.17 * ACOS(COS(RADIANS(:lat))  "
               " * COS(RADIANS(stop_lat))  "
               " * COS(RADIANS(:lon) - RADIANS(stop_lon)) "
               " + SIN(RADIANS(:lat)) "
               " * SIN(RADIANS(stop_lat)))) "
               " AS dist_miles "
               " FROM {0} "
               " ORDER BY dist_miles "
    ).format(table)
    return clause


def sqlite_query_nearest_stops(conn, lon, lat, count, schema, table):
    """ execute the query...
    """
    if count is None or count > 250:
        count = 10
    clause  = sqlite_nearest_query(schema, table)
    ret_val = conn.execute(clause, {'lon':lon, 'lat':lat}).fetchmany(count)
    return ret_val


def postgres_check_db(db_name, db_user, db_table=None):
    """
    """
    ret_val = True
    con = None
    try:
        from psycopg2 import connect

        # step 1: check the database connection
        con = connect(user=db_user, dbname=db_name)

        # step 2: (optionally) check a value from a given database
        if db_table:
            cur = con.cursor()
            cur.execute('SELECT 1 from {}'.format(db_table))
            item = cur.fetchone()
            log.debug("POSTGRES item {} from table {} of db {}".format(item, db_table, db_name))
    except Exception as e:
        log.error("POSTGRES DATABASE ERROR : {}".format(e))
        ret_val = False
    finally:
        if con:
            con.close()
    return ret_val


def postgres_add_postgis(db_name, db_user):
    """ add postgis extension on a named database
    """
    ret_val = True
    con = None
    try:
        from psycopg2 import connect
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        con = connect(user=db_user, dbname=db_name)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute('CREATE EXTENSION postgis')
        cur.close()
        con.close()
        con = None
    except Exception as e:
        log.error("POSTGRES DATABASE ERROR : {}".format(e))
        ret_val = False
    finally:
        if con:
            con.close()
    return ret_val


def postgres_create_db(db_name, db_user):
    """ create a postgres db...and also maybe add the postgis extension
    """
    ret_val = True
    con = None
    try:
        from psycopg2 import connect
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        # step 1: connect to global postgres database and then create new db
        con = connect(user=db_user, dbname='postgres')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute('CREATE DATABASE {}'.format(db_name))
        cur.close()
        con.close()
        con = None
    except Exception as e:
        log.error("POSTGRES DATABASE ERROR : {}".format(e))
        ret_val = False
    finally:
        if con:
            con.close()
    return ret_val


def postgres_check_create_db(db_name, db_user, is_geospatial=False):
    """
    """
    ret_val = True
    try:
        exists = postgres_check_db(db_name, db_user)
        if not exists:
            ret_val = postgres_create_db(db_name, db_user)
            if ret_val and is_geospatial:
                ret_val = postgres_add_postgis(db_name, db_user)
    except Exception as e:
        log.error("POSTGRES CREATE DATABASE ERROR : {}".format(e))
        ret_val = False

    return ret_val


def postgres_drop_schema(db_url, db_user, move=False):
    """ drop / rename
        TODO: more work needed here
    """
    ret_val = True
    try:
        if move:
            ret_val = postgres_add_postgis(db_name, db_user)
        else:
            pass
    except Exception as e:
        log.error("POSTGRES DROP (RENAME) DATABASE ERROR : {}".format(e))
        ret_val = False

    return ret_val


def postgres_add_shp_file(db_url, db_user, is_geospatial=False):
    """
        @see http://geospatialpython.com/2016/08/pure-python-loading-shapefiles-into.html
    """
    ret_val = True


def session_flush(session):
    """
    clear out a session with a commit and flush
    """
    try:
        session.commit()
        session.flush()
    except Exception as e:
        log.warn(e)


def localhost(url=None, def_val="postgresql://ott@localhost:5432/ott"):
    """
    short hand for localhost url
    """
    ret_val = def_val
    if url:
        ret_val = url
        if url in {'l', 'loc', 'local'}:
            ret_val = def_val
    return ret_val


def check_localhost(url):
    return localhost(url)