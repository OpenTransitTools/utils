import logging
log = logging.getLogger(__file__)


try:
    from geoalchemy2 import Geometry
    from geoalchemy2.functions import GenericFunction

    class ST_ExteriorRing(GenericFunction):
        name = 'ST_ExteriorRing'
        type = Geometry


    class ST_MakePolygon(GenericFunction):
        name = 'ST_MakePolygon'
        type = Geometry


    class ST_Collect(GenericFunction):
        name = 'ST_Collect'
        type = Geometry

except Exception as e:
    log.info(e)


def does_point_intersect_geom(session, point, geom, buffer=0.0):
    """
    return true or false whether point is in / out of the geom
    """
    log.debug('does point intersect this geom')
    ret_val = False
    try:
        ret_val = session.scalar(geom.ST_Intersects(point))
    except Exception as e:
        log.warn(e)

    return ret_val


def point_to_geom_distance(session, point, geom):
    """
    return true or false whether point is in / out of the geom
    """
    log.debug("distance between point and a geom (assuming they don't intersect")
    ret_val = False
    try:
        ret_val = session.scalar(geom.ST_Intersects(point))
    except Exception as e:
        log.warn(e)
    return ret_val
