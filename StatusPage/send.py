import logging
import urllib3
import json
from .exceptions import Error
from .exceptions import CreatePoolManagerFailure
from .exceptions import RequestError
from .exceptions import HttpRequestError
try:  # load the certifi module for SSL certificate validation
    import certifi
except Exception:  # load failed, so initialize the connecton pool appropriately
    no_certifi_load = True
else:
    no_certifi_load = False

__version__ = "1.2.0"
__author__ = "chris.hare@icloud.com"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.info("%s Module Version %s/%s", __name__, __version__, __author__)

statusNames = ("operational", "under_maintenance", "degraded_performance",
               "partial_outage", "major_outage")

if no_certifi_load is True:  # initialize the Pool Manager
    logging.warning("certifi is not available.")
    try:
        pool = urllib3.PoolManager()
    except Exception as e:
        raise ConnectionError(e)
else:  # load certifi with the Pool Manager
    logging.debug("certifi loaded")
    try:
        pool = urllib3.PoolManager(ca_certs=certifi.where())
    except Exception as e:
        raise ConnectionError(e)


def status(event):
    """use the update_component api to indicate the endpoint is operational"""

    logger.debug("event = %s", event)

    if event.get('url', None) is None:
        raise AttributeError("url not specified")

    if event.get('status') not in statusNames:
        logger.error("invalid status: %s", event.get('status'))
        raise ValueError("invalid status")

    apiUrl = f"{event.get('baseUrl')}/pages/{event.get('pageid')}/components/{event.get('componentid')}"

    fields = {
        'component': {
            'status': event.get('status'),
        }
    }

    try:
        response = pool.request(
            'PATCH',
            apiUrl,
            body=json.dumps(fields),
            headers={"Authorization": f"OAuth {event.get('apikey')}"},
            retries=int(event.get('retries', 3)),
            timeout=float(event.get('timeout', 3)))
    except Exception as e:
        raise ConnectionError(e)

    logger.debug(json.loads(response.data.decode("utf-8")))

    return (response)


# end

