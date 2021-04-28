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
try:
    import StatusPage
except Exception as error:
    print(f"import StatusPage: {error}")
    sys.exit(1)
# import StatusPage

__version__ = "1.0.22"
__author__ = "labrlearning.medium.com"
__copyright__ = "(C) 2021 Chris Hare"
logger = logging.getLogger()
logger.setLevel("INFO")
logging.basicConfig(
    level=logging.INFO,
    format=
    "%(asctime)s %(levelname)-8s %(module)s.%(funcName)s.%(lineno)d %(message)s",
)

CONFIG = "endpoints.yaml"


def main():
    """
    main: main processing loop
    """

    logger.info("%s Module Version %s/%s", __name__, __version__, __author__)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("CloudWatch").setLevel(logging.WARNING)
    logging.getLogger("Check").setLevel(logging.WARNING)
    logging.getLogger("StatusPage").setLevel(logging.WARNING)

    # load the endpoint config file, endpoints.yaml
    if os.path.isfile(CONFIG) is False:
        logger.critical("config: %s not found.", CONFIG)
        raise FileNotFoundError
    # open the file and read the contents
    with open(CONFIG, "r") as f:
        config = yaml.safe_load(f)

    connectionTimeout = float(config.get('connection').get('timeout'))
    connectionRetries = int(config.get('connection').get('retries'))

    logger.info("Initializing loop")
    # TODO: This code doesn't yet know how to send a POST with a 
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
                "componentid": endpoint.get("componentid", None),
                "pageid": config.get("statuspage").get("pageId", None),
                "baseUrl": config.get("statuspage").get("baseUrl", None),
                "apikey": config.get("statuspage").get("apiKey", None),
            }
            # connect to the endpoint, well, try to
            response = Check.status(event)
            logger.debug("endpoint response: %s expected: %s",
                         response.get('endpoint').get('status'),
                         endpoint.get('status'))
            # if the endpoint response is not what we are expecting, 
            #    log a warning
            #    send the major_outage notification to statuspage if configured
            #
            if response.get('endpoint').get('status') != endpoint.get('status'):
                logger.warning("endpoint response: %s expected: %s",
                               response.get('endpoint').get('status'),
                               endpoint.get('status'))
            if response.get('endpoint').get('status') == endpoint.get(
                    'status'):
                event['status'] = "operational"
                StatusPage.status(event)

            if config.get('cloudwatch').get('namespace', None) is not None:
                try:
                    cw_response = CloudWatch.put(
                        Namespace=config.get('cloudwatch').get(
                            'namespace', None),
                        Data=response)
                except AttributeError as e:
                    logger.error('failed to write cloudwatch metrics: %s', e)
            else:
                logger.warning("cloudwatch metrics disabled by configuration")
                cw_response = {}

            if __name__ == "__main__":
                click.secho(
                    (
                    f"endpoint: {response.get('url')} " 
                    f"status: {response.get('endpoint').get('message')} "
                    f"({response.get('endpoint').get('status')}) "
                    f"time: {response.get('endpoint').get('time'):.2f}ms "
                    f"metrics: {cw_response.get('body', 'disabled')} "
                    f"{cw_response.get('statusCode', '')}"
                    ),
                    fg='cyan')
                
            logger.info(
                "endpoint: %s status: %s(%s) time: %s ms metrics: %s(%s)",
                response.get("url"),
                response.get("endpoint").get("message"),
                response.get("endpoint").get("status"),
                response.get("endpoint").get("time"),
                cw_response.get("body", None),
                cw_response.get("statusCode", None), )
            # end of for
        # sleep
        if config.get('monitor').get('delay') == 0:
            logger.info("execution complete")
            return {'status': 200, 'body': 'executin complete'}

        logger.info("pausing for %s seconds",
                    config.get('monitor').get('delay', 60))
        sys.exit(9)
        time.sleep(config.get('monitor').get('delay', 60))
        # end of while
    # end of def


if __name__ == "__main__":
    
    import optparse
    import click
    
    optionList = {}
    parser = optparse.OptionParser("usage: %prog [options] arg1 arg2")
    
    parser.add_option("-f", "--file", 
        dest="CONFIG",
        default="endpoints.yaml", 
        type="string",
        help="specify the configuration YAML file")
    
    parser.add_option("-l", "--log", 
        dest="logfile",
        type="string",
        help="specify the local log file.  If not specified, it is disabled.")

    parser.add_option("-v", "--version", 
        dest="version",
        action="store_true",
        help="print version information")    

    # args should be empty because only options are used
    (options, args) = parser.parse_args()
    logger.debug("options = %s", options)
    # add addtional options
    CONFIG = options.CONFIG

    if options.version is True:
        click.secho(f"{os.path.basename(sys.argv[0])} Version {__version__}/{__author__}", fg='yellow')
        click.secho(f"{__copyright__}", fg='yellow')
        sys.exit(0)

    # if no log file is specified, then don't enable the log 
    # file handler and don't disable the console log
    if options.logfile is not None:
        # Configure the log file
        lhStdout = logger.handlers[0]  # stdout is the only handler initially
        fh = logging.FileHandler('monitor.log')
        formatter=logging.Formatter("%(asctime)s %(levelname)-8s %(module)s.%(funcName)s.%(lineno)d %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.removeHandler(lhStdout)
        logger.propogate = False
    
    try:
        main()
    except FileNotFoundError:
        click.secho(f"The provided configuration file '{options.CONFIG}' does not exit.", fg='red')
        sys.exit(1)
        
    click.secho("execution complete.", fg='green')

