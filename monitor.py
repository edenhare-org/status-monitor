# synthetics
import sys
import logging
import time
import signal
import Check
import CloudWatch
# import StatusPage

__version__="1.0.0"
__author__="chris.hare@icloud.com"
logger = logging.getLogger()
logger.setLevel('INFO')
logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(module)s.%(funcName)s.%(lineno)d %(message)s')
logger.propagate = True
logger.info("%s Module Version %s/%s", __name__, __version__, __author__)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('CloudWatch').setLevel(logging.DEBUG)
logging.getLogger('Check').setLevel(logging.DEBUG)

loopDelay = 300

def keyboardInterruptHandler(signal, frame):
    """catch the keyboard interrupt

    Args:
        signal (signal): the signal name to intercept
        frame ([type]): [description]
    """
    logging.critical(
        "KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(
            signal)
    )
    exit(0)

def main():
    try:
        import endpoints as Endpoints
    except Exception as e:
        logger.critical("cannot import endpoints: %s", e)
        sys.exit(1)

    connectionTimeout = float(Endpoints.connectionTimeout)
    connectionRetries = int(Endpoints.connectionRetries)

    logger.info("Initializing loop") 
    while True:
        for c, endpoint in enumerate(Endpoints.apiList):
            event = {
                'url': endpoint.get('url', None),
                'method': endpoint.get('method', 'GET'),
                'timeout': connectionTimeout,
                'retries': connectionRetries,
                'loglevel': endpoint.get('loglevel', 'INFO'),
                'body': endpoint.get('body', None),
                'headers': endpoint.get('headers', None),
                'auth': endpoint.get('auth', None)
            }

            response = Check.status(event, '')
            
            cw_response = CloudWatch.put(response, '')

            logger.info("endpoint: %s status: %s(%s) time: %s ms metrics: %s(%s)", 
                response.get('url'),
                response.get('endpoint').get('message'),
                response.get('endpoint').get('status'),
                response.get('endpoint').get('time'),
                cw_response.get('body'),
                cw_response.get('statusCode')
            )
            # end of for    
        # sleep
        logger.info("pausing for %s seconds", loopDelay)
        time.sleep(loopDelay)
        # end of while       
    # end of def

if __name__ == "__main__":
    main()
