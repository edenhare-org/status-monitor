# synthetics
import os
import logging
import json
import botocore
import boto3

__version__="1.0.0"
__author__="chris.hare@icloud.com"
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
logger.info("%s Module Version %s/%s", __name__, __version__, __author__)
logger.info("boto3 version %s", boto3.__version__)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)

def put(event, context):

    e = ''
    namespace = 'Synthetics'
        
    try:
        client = boto3.client("cloudwatch")
    except Exception as e:
        logger.critical("cannot create cloudwatch client: %s", e)
        return {'statusCode': 500, 'error': "Cannot create Cloudwatch client"}

    if event.get('url', None) is None:
        logger.error('no url in argument list')
        return {'statusCode': 500, 'error': "no url in argument list"}

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


if __name__ == "__main__":
    response = handler({}, "")
    print(json.dumps(response, indent=2))

