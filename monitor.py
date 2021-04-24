"""
monitor.py
This module performs the work to check the configured endpoints
"""
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0612
# synthetics
import sys
import logging
import time
import Check
import CloudWatch
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
    import endpoints as Endpoints
except Exception as e:
    logger.critical("cannot import endpoints: %s", e)
    sys.exit(1)

def main():
    """
    main: main processing loop
    """
    loopDelay = 300
    connectionTimeout = float(Endpoints.connectionTimeout)
    connectionRetries = int(Endpoints.connectionRetries)

    logger.info("Initializing loop")
    while True:
        for c, endpoint in enumerate(Endpoints.apiList):
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

            response = Check.status(event)

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
        logger.info("pausing for %s seconds", loopDelay)
        time.sleep(loopDelay)
        # end of while
    # end of def


if __name__ == "__main__":
    main()
