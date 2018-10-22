class OtpTiBase(object):
    """
    Base class for OpenTripPlanner (OTP) Transit Index (TI) web services

    Park & Rides:
        https://<domain & port>/otp/routers/default/park_and_ride

    Routes and Routes serving a stop:
        https://<domain & port>/otp/routers/default/index/routes
        https://<domain & port>/otp/routers/default/index/stops/TriMet:5516/routes

    Stops:
        https://<domain & port>/otp/routers/default/index/stops?
          minLat=45.50854243338104&maxLat=45.519789433696744&minLon=-122.6960849761963&maxLon=-122.65591621398927

        https://<domain & port>/otp/routers/default/index/stops?
          radius=1000&lat=45.4926336&lon=-122.63915519999999

    Stop Schedules:
        https://<domain & port>/otp/routers/default/index/stops/TriMet:823/stoptimes?timeRange=14400
    """
    def __init__(self, args={}):
        self.set_attribute_via_dict('agencyName', args)
        self.set_attribute_via_dict('id', args)
        self.set_attribute_via_dict('name', args)
        self.set_attribute_via_dict('lat', args)
        self.set_attribute_via_dict('lon', args)
        self.set_attribute_via_dict('url', args)

    def set_attribute_via_dict(self, name, vals, always_cpy=False, def_val=None):
        from .. import object_utils
        object_utils.safe_set_from_dict(self, name, vals, always_cpy, def_val)
