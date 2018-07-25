from ott.utils.dao.base import DatabaseNotFound
from ott.utils.dao.base import ServerError


# only need to create these classes once...
DATA_NOT_FOUND_MSG = DatabaseNotFound()
SYSTEM_ERROR_MSG = ServerError()


# cache time - affects how long varnish cache will hold a copy of the data
CACHE_LONG = 36000  # 10 hours
CACHE_SHORT = 600  # 10 minutes
