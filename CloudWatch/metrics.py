"""
metrics.py - publish cloudwatch maetrics
"""
# synthetics
# Disable Variable name doesn't conform to snake_case naming style (invalid-name)
# pylint: disable=C0103
# Disable Catching too general exception Exception (broad-except)
# pylint: disable=W0703

import logging
import boto3

__version__="1.0.0"
__author__="chris.hare@icloud.com"
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
logger.info("%s Module Version %s/%s", __name__, __version__, __author__)
logger.info("boto3 version %s", boto3.__version__)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)

def put(**kwargs):
    """
    put - public a cloudwatch metric

    Args:
        event (dict): required information to publish the metric

    Returns:
        dict: the response with the publish results
    """
    e = ''
    event = kwargs.get('Data', None)
    namespace = kwargs.get('Namespace', None)

    if event.get('url', None) is None:
        raise AttributeError ('no url in argument list')
        logger.error('no url in argument list')
        return {'statusCode': 500, 'error': "no url in argument list"}
    
    if namespace is None:
        raise AttributeError ('no namespace provided in argument list')
        
    try:
        client = boto3.client("cloudwatch")
    except Exception as e:
        logger.critical("cannot create cloudwatch client: %s", e)
        return {'statusCode': 500, 'error': "Cannot create Cloudwatch client"}

    if event.get('endpoint').get('time', 0) == 0:
        logger.warning('%s: response time = 0', event.get('url', None))

    try:
        response = client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    "MetricName":
                    "ResponseTime",
                    "Dimensions": [
                        {
                            "Name": "EndPoint",
                            "Value": event.get('url', None)
                        },
                    ],
                    "Timestamp":
                    event.get('timestamp', None),
                    "Value":
                    event.get('endpoint').get('time', 0),
                    "Unit":
                    "Milliseconds",
                },
                {
                    "MetricName":
                    event.get('endpoint').get('message', "Unknown"),
                    "Dimensions": [
                        {
                            "Name": "EndPoint",
                            "Value": event.get('url', None)
                        }
                    ],
                    "Timestamp":
                    event.get('timestamp', None),
                    "Value":
                    1,
                    "Unit":
                    "Count",
                },
            ], )
    except Exception as e:
        logger.error("Error posting cloudwatch metric: %s", e)
        return {
            'statusCode': 500,
            'body': f"Cannot post to CloudWatch metrics: {e}",
            'url': event.get('url', None),
            'error': e
        }

    logger.debug("response = %s", response)

    return {
        'statusCode': 200,
        'body': "OK",
        'url': event.get('url'),
        'error': e,
        'timestamp': event.get('endpoint').get('time'),
        'endpoint': {
            'status': event.get('endpoint').get('status'),
            'message': event.get('endpoint').get('message'),
            'time': event.get('endpoint').get('time')
        }
    }
# end
