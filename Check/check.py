"""
check.py - evaluate the status of the specified endpoint.

Returns:
    dict: response dictionary
        {
        'statusCode': response status code,
        'body': response status text,
        'url': url,
        'error': error message if any,
        'timestamp': timestamp,
        'endpoint': {
            'status': endpoint status code,
            'message': endpoint status message,
            'time': endpoint response time
            }
        }
"""

# synthetics
# pylint: disable=C0103
# Disable Catching too general exception Exception (broad-except)
# pylint: disable=W0703
# Disable Access to a protected member
# pylint: disable=W0212
import logging
import time
import datetime
import urllib3
from .exceptions import Error
from .exceptions import CreatePoolManagerFailure
from .exceptions import RequestError
from .exceptions import HttpRequestError

__version__ = "1.4.0"
__author__ = "chris.hare@icloud.com"
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
logging.getLogger('urllib3').setLevel(logging.WARNING)


def status(event):
    """status(event) - evaluate the status of the specified endpoint

    Args:
        event ([dict]): dictionary with required information

    Returns:
        [dict]: response information
    """
    e = ''

    try:
        logger.setLevel(event.get('loglevel'))
        logging.getLogger('urllib3').setLevel(event.get('loglevel'))
    except:
        pass
    try:
        pool = urllib3.PoolManager()
    except Exception as e:
        raise CreatePoolManagerFailure(e)

    if event.get('url', None) is None:
        raise AttributeError("url not specified")

    # The code doesn't know how to handle POST
    # The code doesn't know how to handle these yet

    st = time.perf_counter()
    try:
        response = pool.request(
            event.get('method', 'GET'),
            event.get('url', None),
            retries=int(event.get('retries', 3)),
            timeout=float(event.get('timeout', 3)))
    except Exception as e:
        raise HttpRequestError(e)

    responseTime = (time.perf_counter() - st) * 1000

    logger.debug("checking endpoint: %s:%s status=%s bytes=%s time=%.3fms",
                 event.get('method', 'GET'),
                 event.get('url', None), response.status,
                 response._fp_bytes_read, responseTime)

    if response.status >= 200 and response.status <= 299:
        statusMessage = "2xx"
    elif response.status >= 300 and response.status <= 399:
        statusMessage = "3xx"
    elif response.status >= 400 and response.status <= 499:
        statusMessage = "4xx"
    elif response.status >= 500 and response.status <= 599:
        statusMessage = "5xx"
    endpointStatus = response.status

    ts = datetime.datetime.timestamp(datetime.datetime.now())
    
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return {
        'statusCode': 200,
        'body': "OK",
        'url': event.get('url', None),
        'error': e,
        'timestamp': ts,
        'endpoint': {
            'status': endpointStatus,
            'message': statusMessage,
            'time': responseTime
        }
    }


# end

