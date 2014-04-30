import math
from sqlalchemy import event
import logging
log = logging.getLogger(__file__)

def add_math_to_sqllite(conn, conn_record):
    ''' This method is called for each new SQLAlchemy database connection. I'm using it as a connection decorator to
        add math routines to a sqllite database

        @note: check out the call to (above): event.listen(self.engine, 'connect', Database.connection)
        @see:  http://docs.sqlalchemy.org/en/rel_0_8/core/events.html#sqlalchemy.events.PoolEvents
    '''
    if 'sqlite' in type(conn).__module__:        
        print 'in method that adds math to sqllite'
        conn.create_function("sin",     1, math.sin)
        conn.create_function("cos",     1, math.cos)
        conn.create_function("acos",    1, math.acos)
        conn.create_function("sqrt",    1, math.sqrt)
        conn.create_function("pow",     2, math.pow)
        conn.create_function("radians", 1, math.radians)


def decorate_engine(engine):
    event.listen(engine, 'connect', add_math_to_sqllite)


def closest_stops_tuple_to_dict(tup):
    #import pdb; pdb.set_trace()
    ret_val = {
        'stop_id'    : tup[1],
        'stop_name'  : tup[0],
        'stop_lat'   : tup[2],
        'stop_lon'   : tup[3],
        'dist_miles' : tup[4]
    }
    return ret_val


def sqlite_nearest_query(schema=None, table='stops'):
    '''
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
    '''
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
    ''' execute the query...
    '''
    if count is None or count > 250:
        count = 10
    clause  = sqlite_nearest_query(schema, table)
    ret_val = conn.execute(clause, {'lon':lon, 'lat':lat}).fetchmany(count)
    return ret_val

