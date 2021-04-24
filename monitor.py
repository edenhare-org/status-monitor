"""
monitor.py
This module performs the work to check the configured endpoints
"""
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0612
# synthetics
import sys
import os
import logging
import time
try:
    import yaml
except Exception as error:
    print(f"import yaml: {error}")
    sys.exit(1)
try:
    import Check
except Exception as error:
    print(f"import Check: {error}")
    sys.exit(1)
try:
    import CloudWatch
except Exception as error:
    print(f"import CloudwWatch: {error}")
    sys.exit(1)

# import StatusPage

__version__ = "1.0.0"
__author__ = "chris.hare@icloud.com"
logger = logging.getLogger()
logger.setLevel("INFO")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(module)s.%(funcName)s.%(lineno)d %(message)s",
)
logger.propagate = True
logger.info("%s Module Version %s/%s", __name__, __version__, __author__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("CloudWatch").setLevel(logging.DEBUG)
logging.getLogger("Check").setLevel(logging.DEBUG)

try:
#try:
#except Exception as e:
#    logger.critical("cannot import endpoints: %s", e)
#    sys.exit(1)

CONFIG="endpoints.yaml"

def main():
    """
    main: main processing loop
    """
    loopDelay = 300
    
    # load the endpoint config file, endpoints.yaml
    if os.path.isfile(CONFIG) is False:
        logger.critical("config: %s not found.", CONFIG)
        sys.exit(2)
    # open the file and read the contents
    with open(CONFIG, "r") as f:
      config = yaml.safe_load(f)
    print(config)
    print(config.get('apiList'))
    
    connectionTimeout = float(config.get('connection').get('timeout'))
    connectionRetries = int(config.get('connection').get('retries'))
    
    logger.info("Initializing loop")
    #TODO: This code doesn't yet know how to send a POST with a 
    # body and header
    while True:
        for c, endpoint in enumerate(config.get('apiList')):
            event = {
                "url": endpoint.get("url", None),
                "method": endpoint.get("method", "GET"),
                "timeout": connectionTimeout,
                "retries": connectionRetries,
                "loglevel": endpoint.get("loglevel", "INFO"),
                "body": endpoint.get("body", None),
                "headers": endpoint.get("headers", None),
                "auth": endpoint.get("auth", None),
            }
            # connect to the endpoint, well, try to
            response = Check.status(event)
            logger.debug("endpoint response: %s expected: %s",
                response.get('endpoint').get('status'),
                endpoint.get('status')
            )
            if response.get('endpoint').get('status') != endpoint.get('status'):
                logger.warning("endpoint response: %s expected: %s",
                    response.get('endpoint').get('status'),
                    endpoint.get('status')
                )

            cw_response = CloudWatch.put(response)

            logger.info(
                "endpoint: %s status: %s(%s) time: %s ms metrics: %s(%s)",
                response.get("url"),
                response.get("endpoint").get("message"),
                response.get("endpoint").get("status"),
                response.get("endpoint").get("time"),
                cw_response.get("body"),
                cw_response.get("statusCode"),
            )
            # end of for
        # sleep
        sys.exit(9)
        logger.info("pausing for %s seconds", loopDelay)
        time.sleep(loopDelay)
        # end of while
    # end of def


if __name__ == "__main__":
    main()
