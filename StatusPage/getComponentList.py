import logging
import json
import os
import datetime
import urllib3


MODULE_VERSION="getComponentList.1.0.0"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.info("%s Module Version %s", __name__, MODULE_VERSION)
logging.getLogger('urllib3').setLevel(logging.WARNING)


def getComponentList(**kwargs):
    """ retrieve the list of components """
    print(kwargs)
    baseUrl=kwargs.get('BaseUrl', None)
    pageids = kwargs.get('PageIds', None)
    apikey = kwargs.get('ApiKey', 0)
    retries = kwargs.get('Retries', 3)
    timeout = kwargs.get('Timeout', 3)

    if baseUrl is None:
        logger.error("no API url was provided.")
        return {
            'statusCode': 400,
            'body': "ERROR",
            'error': "no api url was provided.",
        } 
    if pageids is None:
        logger.error("No page ids were provided.")
        return {
            'statusCode': 400,
            'body': "ERROR",
            'error': "no pageids we provided.",
        }
    
    try:
        pool = urllib3.PoolManager()
    except Exception as e:
        logger.critical("cannot create http pool manager: %s", e)
        return {
            'statusCode': 500,
            'error': "Cannot create http pool manager"
        }
    
    logger.debug("pageids = %s", pageids)
    cl = []
    for pageid in pageids:
        logger.debug("getting components for pageid %s", pageid)
        try:
            response = pool.request(
                "GET",
                f"{baseUrl}/pages/{pageid}/components",
                headers={"Authorization": f"OAuth {apikey}"},
                retries=int(retries),
                timeout=int(timeout)
            )
        except Exception as e:
            logger.error("cannot retrieve components: %s", e)
        else:
            details = json.loads(response.data.decode("utf-8"))
            print(details)
            cl = [ *cl, *details]

    #details = json.loads(response.data.decode("utf-8"))
    logger.debug("component list = %s", json.dumps(cl, indent=2))

    return cl
