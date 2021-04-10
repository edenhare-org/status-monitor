import urllib3
import logging
import json
import time

MODULE_VERSION="1.0.0"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

logger.info("%s Module Version %s", __name__, MODULE_VERSION)
logger.info("urllib3 version %s", urllib3.__version__)

try:
    pool = urllib3.PoolManager()
except Exception as e:
    raise Execption from e


def check(**kwargs):
    
    url=kwargs.get('Url', None)
    timeout=kwargs.get('Timeout', None)
    retries=kwargs.get('Retries', None)
    ok = kwargs.get('Ok', 200)
    method = kwargs.get('Method', "GET")
    body = kwargs.get('Body', None)
    headers = kwargs.get('Headers', None)
    
    logger.debug(
        "checking endpoint: %s:%s retries=%s timeout=%s",
        method, url, retries, timeout)
    
    st = time.perf_counter()
    try:
        response = pool.request(
            method,
            url,
            retries=int(retries),
            timeout=int(timeout)
        )
    except Exception as error:
        logger.error("error=%s", error)
        raise ValueError (error)
    rTime = (time.perf_counter() - st) * 1000
    # logger.debug(response.__dict__)
    logger.debug(
        "checking endpoint: %s:%s status=%s bytes=%s time=%.3fms",
        method,
        url,
        response.status,
        response._fp_bytes_read,
        rTime
    )
    
    return {
        'status': response.status,
        'time': rTime,
        'bytes': response._fp_bytes_read
    }

