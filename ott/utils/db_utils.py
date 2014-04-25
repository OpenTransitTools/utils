import math

from gtfsdb.model.stop import Stop
from ott.controller.services.model.stop_response import StopResponse


def distance_km(lat1, lon1, lat2, lon2):
    ''' return distance between two points in km using haversine
        http://en.wikipedia.org/wiki/Haversine_formula
        http://www.platoscave.net/blog/2009/oct/5/calculate-distance-latitude-longitude-python/
        Author: Wayne Dyck
    '''
    ret_val = 0
    radius = 6371 # km
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    ret_val = radius * c

    return ret_val

def distance_mi(lat1, lon1, lat2, lon2):
    ''' return distance between two points in miles
    '''
    km = distance_km(lat1, lon1, lat2, lon2)
    return km * 0.621371192


def add_math_to_sqllite(conn, conn_record):
    ''' This method is called for each new SQLAlchemy database connection. I'm using it as a connection decorator to
        add math routines to a sqllite database

        @note: check out the call to (above): event.listen(self.engine, 'connect', Database.connection)
        @see:  http://docs.sqlalchemy.org/en/rel_0_8/core/events.html#sqlalchemy.events.PoolEvents
    '''
    if 'sqlite' in type(conn).__module__:
        #import pdb; pdb.set_trace()
        print 'in method that adds math to sqllite'
        conn.create_function("sin",     1, math.sin)
        conn.create_function("cos",     1, math.cos)
        conn.create_function("acos",    1, math.acos)
        conn.create_function("sqrt",    1, math.sqrt)
        conn.create_function("pow",     2, math.pow)
        conn.create_function("radians", 1, math.radians)


def decorate_engine(engine):
    from sqlalchemy import event
    event.listen(engine, 'connect', add_math_to_sqllite)


def closest_stops_tuple_to_dict(tup):
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



def geoalchemy_query_nearest_stops(session, point, count=10):
    ''' PostGIS / geo
    '''
    #ret_val = session.query(Stop, Stop.geom.distance(point)).order_by(Stop.geom.distance(point)).limit(count)
    ret_val = session.query(Stop).order_by(Stop.geom.distance(point)).limit(count)
    return ret_val

def get_closest_stops(session, lon, lat, count=10, schema=None, table='stops', def_val=[]):
    ''' get_closest_stops(session, -122.593, 45.587) will return stops nearest PDX airport
    '''
    ret_val = []
    conn = session.connection().connection
    try:
        if 'sqlite' in session.bind.dialect.name:
            closest = sqlite_query_nearest_stops(conn, lon, lat, count, schema, table)
            for c in closest:
                stop_id = c[0]
                dist    = c[4]
                s = StopResponse.from_stop_id(stop_id, session, distance=dist)
                if s:
                    ret_val.append(s)
        else:
            point = 'POINT({0} {1})'.format(lon, lat)
            closest = geoalchemy_query_nearest_stops(session, point, count)
            for s in closest:
                stop = s
                dist = distance_mi(stop.stop_lat, stop.stop_lon, lat, lon)
                #print s[1]
                #print dist

                s = StopResponse.from_stop_obj(stop, session, distance=dist)
                if s:
                    ret_val.append(s)
            ret_val.sort(key=lambda x: x.distance, reverse=False)
    except Exception, e:
        print e
    finally:
        ## TODO - need to close connection explicitly? mess up session?
        conn.close() 
        pass
    return ret_val
