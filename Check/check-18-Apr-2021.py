# synthetics
import logging
import json
import urllib3
import time
import datetime

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logging.getLogger('urllib3').setLevel(logging.WARNING)


def handler(event, context):

    e = ''
    loglevel = event.get('LOGLEVEL', 'INFO')
    logger.setLevel(loglevel)
    logger.info("loglevel = %s", logging.getLevelName(logger.level))
    try:
        pool = urllib3.PoolManager()
    except Exception as e:
        logger.critical("cannot create http pool manager: %s", e)
        return {
            'statusCode': 500,
            'body': "Cannot create http pool manager"
        }

    url = event.get('URL', "http://www.labr.net")

    if url is None:
        logger.error("url not specified")
        return {
            'statusCode': 500,
            'body': "url not specified"
        }
    #! The code doesn't know how to handle POST
    method = event.get('METHOD', 'GET')
    timeout = event.get('TIMEOUT', 3)
    retries = event.get('RETRIES', 3)

    #! The code doesn't know how to handle these yet
    body = event.get('BODY', None)
    headers = event.get('HEADERS', None)
    auth = event.get('AUTH', None)


    st = time.perf_counter()
    try:
        response = pool.request(
            method,
            url,
            retries=int(retries),
            timeout=int(timeout)
        )
    except Exception as e:
        logger.error("error=%s", e)
        return {
            'statusCode': 500,
            'body': f"Request to {url} failed: {e}",
            'url': url,
            'error': e
        }
    responseTime = (time.perf_counter() - st) * 1000

    logger.debug(
        "checking endpoint: %s:%s status=%s bytes=%s time=%.3fms",
        method,
        url,
        response.status,
        response._fp_bytes_read,
        responseTime
    )

    if response.status >= 200 and response.status <= 299:
        status = "2xx"
    if response.status >= 300 and response.status <= 399:
        status = "3xx"
    if response.status >= 400 and response.status <= 499:
        status = "4xx"
    if response.status >= 500 and response.status <= 599:
        status = "5xx"
    endpointStatus = response.status

    ts = datetime.datetime.timestamp(datetime.datetime.now())

    return {
        'statusCode': 200,
        'body': "OK",
        'url': url,
        'error': e,
        'timestamp': ts,
        'endpoint': {
            'status': endpointStatus,
            'message': status,
            'time': responseTime
        }
    }

if __name__ == "__main__":
    response = handler({}, "")
    print(json.dumps(response, indent=2))
