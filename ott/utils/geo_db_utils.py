import db_utils
import logging
log = logging.getLogger(__file__)


try:
    from geoalchemy2 import Geometry
    from geoalchemy2.functions import GenericFunction
    from sqlalchemy.sql.functions import func

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
    ret_val = False
    try:
        ret_val = session.scalar(geom.ST_Intersects(point))
    except Exception as e:
        log.warn(e)
        db_utils.session_flush(session)
    return ret_val


def point_to_geom_distance(session, point, geom):
    """
    return true or false whether point is in / out of the geom
    """
    ret_val = -111.111
    try:
        ret_val = session.scalar(func.ST_distance(func.st_buffer(point, 0.00001), geom))
    except Exception as e:
        log.warn(e)
        db_utils.session_flush(session)
    return ret_val
