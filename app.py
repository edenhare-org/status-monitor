import os
import sys
import time
import datetime
import logging
import json
from configparser import ConfigParser
import optparse


# set logging configuration
# See https://randops.org/2017/09/26/pythons-logging-module-in-a-boto3botocore-context/
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.propagate = True
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(module)s.%(funcName)s.%(lineno)d %(message)s')
# set log level for specific imported modules
logging.getLogger('urllib3').setLevel(logging.WARNING)

CONFIGFILE="bad.ini"
TIMEOUT=5
RETRIES=10
MODULE_VERSION="1.0.0"
logger.info("%s Module Version %s", __name__, MODULE_VERSION)
logger.info("Current loglevel = %s", logging.getLevelName(logger.level))

try:
    import endpoint
except Exception as error:
    print(f"FATAL: Import error for endpoint.py: {error}")
    sys.exit(1)
else:
    logging.getLogger('endpoint').setLevel(logging.INFO)

import tracking
logging.getLogger('tracking').setLevel(logging.INFO)


def loadConfiguration(**kwargs):

    # get the directory where the script is running
    scriptDir = os.getcwd()  
    
    # Use the ini file passed in.  
    ini = kwargs.get('Config', CONFIGFILE)

    # Check if there is a path on the file
    d = os.path.dirname(ini)
    if d is None:
        # there is no path 
        iniPath = f"{scriptDir}/{ini}"
    else:
        # there is a path
        iniPath = ini
    
    logger.debug("Using configuration file = %s", iniPath)
    logger.debug("file directory = %s", d)
    logger.debug("CWD = %s", scriptDir)
    
    # verify the file exists
    if os.path.exists(iniPath) is False:
        raise OSError (f"{ini} file not found.")
    
    # we have a file which exists, so parse it
    parser = ConfigParser()
    parser.read(ini)
    
    # save the paraneters in a dict
    config = {}
    for section_name in parser.sections():
        logger.debug('Processing section: %s', section_name)
        if section_name not in config:
            config[section_name] = {}
        for name, value in parser.items(section_name):
            # logger.debug('%s.%s = %s', section_name, name, value)
            if value == "True":
                value = True
            elif value == "False":
                value = False
            elif value == "":
                # if there is no value for the key, set the value to None
                value = None
            try:
                config[section_name][name] = value
            except KeyError:
                logger.error("cannot add config.%s.%s = %s", section_name, name, value)
            # else:
                # logger.debug('%s.%s = %s', section_name, name, value)
    
    logger.debug("Config = %s", config)
    return config    
    
    
def parseOptions():
    
    optionList = {}
    parser = optparse.OptionParser("usage: %prog [options] arg1 arg2")
    
    parser.add_option("-f", "--file", 
        dest="configFile",
        default="config.ini", 
        type="string",
        help="specify the config.ini file")

    # args should be empty because only options are used
    (options, args) = parser.parse_args()
    logger.debug("options = %s", options)
    # add addtional options
    optionList['ini'] = options.configFile

    return optionList
    

def insertConfigOptions(**kwargs):
    
    config = kwargs.get('Config', None)
    options = kwargs.get('Options', None)

    if config is None or options is None:
        raise AttributeError("missing config or options")
    
    for name, value in options.items():
        try:
            config['options'][name] = value
        except KeyError as e:
            config['options'] = {}
            config['options'][name] = value
            #logger.debug("created config.options")
        else:
            logger.debug("inserted config.options.%s = %s", name, value)

    return config
    

def buildTargets(**kwargs):

    targets = {}
    
    config = kwargs.get('Config', None)
    
    if config is None:
        raise AttributeError("no config properties")
    
    for section, value in config.items():
        # logger.debug("section: %s value: %s", section, value)
        if 'url' in value:
            logger.debug("found target: %s", value)
            targets[section] = {}
            targets[section]['name'] = section
            
            for item in value.items():
                #logger.debug("0=%s 1=%s", item[0], item[1])
                targets[section][item[0]] = item[1]

            #logger.debug("targets = %s", targets)
    
    return targets


def changeLogLevel(**kwargs):
    
    config = kwargs.get('Config', None)
        
    if config is None:
        raise AttributeError("no config properties")
    
    # if loglevel is specified in the configuration file and it is different
    # from the current log level, change the level
    if ('loglevel' in config['Default']) and (logging.getLevelName(logger.level) != config.get('Default').get('loglevel')):
        logging.warning("Changing log level from %s to %s", 
            logging.getLevelName(logger.level),
            config.get('Default').get('loglevel'))
        logger.setLevel(config.get('Default').get('loglevel'))
        logger.warning("New loglevel = %s", logging.getLevelName(logger.level))
    
    return None


def evaluateEndpoint(**kwargs):
    
    key = kwargs.get('Name', None)
    value = kwargs.get('Data', None)
    config = kwargs.get('Config', None)
    
    endpointName = key
    endpointUrl = value.get('url')
    endpointTimeout = value.get('timeout',
        config.get('Default').get('timeout', TIMEOUT))
    endpointRetries = value.get('retries',
        config.get('Default').get('retries', RETRIES))
    endpointOK = value.get('okcode', 200)
    endpointMethod = value.get('method', "GET")
    endpointBody = value.get('body', None)
    endpointHeaders = value.get('headers', None)
                
    logger.info("Processing %s", endpointName)
    logger.debug("%s: url=%s timeout=%s retries=%s",
        endpointName, endpointUrl, endpointTimeout,
        endpointRetries)

    logger.debug("Connecting to endpoint: %s", endpointUrl)
    
    response = endpoint.check(Url=endpointUrl,
        Timeout=endpointTimeout,
        Retries=endpointRetries,
        Ok=endpointOK,
        Method=endpointMethod,
        Body=endpointBody,
        Headers=endpointHeaders
        )

    if int(response.get('status')) != int(endpointOK):
        text = "down"
    else:
        text = "up"
    logger.info("url=%s, status=%s (%s) time=%.3fms bytes=%d", 
        endpointUrl, text, response.get('status'), 
        response.get('time'), response.get('bytes'))   
        
    return {
         'status': response.get('status'),
         'text': text,
         'time': response.get('time'),
         'bytes': response.get('bytes')
     } 


def main():
    
    if len(sys.argv) > 0:
        logger.warning("Found command line arguments to parse.")
        options = parseOptions()
    
    # if we got a configuration file specified on the command line, use that
    if options is not None:
        ini = options.get('ini', CONFIGFILE)

    try: # load the configuration file
        config = loadConfiguration(Config=ini)
    except OSError as e: # the file is not found
        logger.critical("Exit: %s", e)
        sys.exit(1)        
    except Exception as e: # an unspecified error occurred
        logger.critical("Exit: %s", e)
        sys.exit(1)
    
    try:
        changeLogLevel(Config=config)
    except Exception as e:
        logging.error("Cannot change loglevel: %s", e)

    try:
        config = insertConfigOptions(Config=config, Options=options)
    except Exception as e:
        logger.error("error processing options: %s", e)

    # look for monitoring targets in config.  
    try:
        targets = buildTargets(Config=config)
    except Exception as e:
        logger.error("Target creation error: %s", e)
    
    if targets is None:
        logger.error("target list is empty")
        sys.exit(1)
    
    # do we need to enable Cloudwatch?
    if config.get('Default').get('cloudwatch', False) is True:
        try:
            import cloudwatch
        except Exception as e:
            logger.critical("error importing cloudwatch: %s", e)
            config['Default']['cloudwatch'] = False
        else:
            logging.getLogger('cloudwatch').setLevel(logging.INFO)
    else:
        logger.warning('cloudwatch disabled by configuration')
        cloudwatch = None
        
    if config.get('Default').get('alerts', False) is True:
        try:
            import alerts
        except Exception as e:
            logger.critical("error importing alerts: %s", e)
            config['Default']['alerts'] = False
        else:
            logging.getLogger('alerts').setLevel(logging.DEBUG)    
    else:
        logger.warning('alerts disabled by configuration')
        alerts = None
    
            
    while True:
        logger.debug("top of while")
        
        # need to check for updated config file
        
        for key, value in targets.items():
            checkTime = datetime.datetime.utcnow().timestamp()
            status = evaluateEndpoint(Name=key, Data=value, Config=config)

            if cloudwatch:
                try:
                    cloudwatch.putMetric(
                        Save=config.get('Default').get('cloudwatch', False),
                        Endpoint = value.get('Name', key),
                        Namespace = config.get('Cloudwatch').get('namespace', None),
                        ResponseTime = status.get('time'))
                except Exception as e:
                    logger.critical("error posting to cloudwatch: %s", e)
                    logger.critical("Disabling cloudwatch")
                    config['Default']['cloudwatch'] = False
            else:
                logger.info("Cloudwatch metrics disabled by configuration")
        
            # record site status
            try:
                response = tracking.save(
                        Endpoint=key,
                        State=status.get('text'),
                        ResponseTime=status.get('time'),
                        CheckTime=checkTime,
                        Down=value.get('downthreshold',
                            config.get('Default').get('downthreshold')),
                        Degraded=value.get('degradedthreshold',
                            config.get('Default').get('degradedthreshold'))
                    )
            except Exception as e:
                logger.error("tracking error: %s", e)

            # Alert if required
            if alerts:
                alerts.notify(
                    Alerts=config.get('Default').get('alerts', False),
                    Send=response.get('alert'),
                    Status=status.get('status'),
                    Name=status.get('text'),
                    Time=status.get('time'),
                    Endpoint=key,
                    Url=value.get('url', None),
                    AlertConfig=config.get('Alerts'),
                    EmailConfig=config.get('Email')
                    )
            else:
                logger.info("alerts disabled by configuration")
            # end for loop
            
        logger.info("Next check in %s seconds",
            config.get('Default').get('delay',300))
        
        sys.exit(0)
        
        time.sleep(int(config.get('Default').get('delay',300)))
        logger.debug("Wake Up!")
        # end while

if __name__ == "__main__":
    main()

