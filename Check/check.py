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
# Disable Access to a protected member _fp_bytes_read of a client class (protected-access)
# pylint: disable=W0212
import logging
import time
import datetime
import urllib3

__version__="1.0.0"
__author__="chris.hare@icloud.com"
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
logger.info("%s Module Version %s/%s", __name__, __version__, __author__)
logger.info("urllib3 version %s", urllib3.__version__)
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
        pool = urllib3.PoolManager()
    except Exception as e:
        logger.critical("cannot create http pool manager: %s", e)
        return {
            'statusCode': 500,
            'body': "Cannot create http pool manager"
        }

    if event.get('url', None) is None:
        logger.error("url not specified")
        return {
            'statusCode': 500,
            'body': "url not specified"
        }
    #! The code doesn't know how to handle POST
    #! The code doesn't know how to handle these yet
    # body = event.get('body', None)
    # headers = event.get('headers', None)
    # auth = event.get('auth', None)

    st = time.perf_counter()
    try:
        response = pool.request(
            event.get('method', 'GET'),
            event.get('url', None),
            retries=int(event.get('retries', 3)),
            timeout=float(event.get('timeout', 3))
        )
    except Exception as e:
        logger.error("error=%s", e)
        return {
            'statusCode': 500,
            'body': f"Request to {event.get('url', None)} failed: {e}",
            'url': event.get('url', None),
            'error': e
        }
    responseTime = (time.perf_counter() - st) * 1000

    logger.debug(
        "checking endpoint: %s:%s status=%s bytes=%s time=%.3fms",
        event.get('method', 'GET'),
        event.get('url', None),
        response.status,
        response._fp_bytes_read,
        responseTime
    )

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
