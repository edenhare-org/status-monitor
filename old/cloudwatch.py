import logging
import json
import datetime
import boto3

MODULE_VERSION="1.0.0"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

logger.info("%s Module Version %s", __name__, MODULE_VERSION)
logger.info("boto3 version %s", boto3.__version__)
# set log level for specific imported modules
logging.getLogger('boto3').setLevel(logging.INFO)

try:
    client = boto3.client("cloudwatch")
except Exception as e:
    logger.critical("cannot create cloudwatch client: %s", e)
    raise ConnectionError from e


def putMetric(**kwargs):
    
    logger.debug(kwargs)
    save = kwargs.get('Save', False)
    endpoint = kwargs.get("Endpoint", None)
    namespace = kwargs.get('Namespace', None)
    responseTime = kwargs.get("ResponseTime", 0)
    
    if save is False:
        logger.warning("metric push is disabled by configuration")
        return None
    if namespace is None:
        logger.error("Namespace is None")
        return None
    
    try:
        response = client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    "MetricName": "ResponseTime",
                    "Dimensions": [
                        {
                            "Name": "EndPoint",
                            "Value": endpoint.replace(" ", "")
                        },
                    ],
                    "Timestamp": datetime.datetime.timestamp(datetime.datetime.now()),
                    "Value": responseTime,
                    "Unit": "Milliseconds",
                },
            ],
        )
    except Exception as e:
        logger.error(e)
        raise Exception from e
    
    logging.debug("response = %s", response)
    
    if response.get('ResponseMetadata').get('HTTPStatusCode', None) == 200:
        logger.info("metric push success")
    else:
        logger.info("metric push failure (%s)",
            response.get('ResponseMetadata').get('HTTPStatusCode'))
    
    return None

    

