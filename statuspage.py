# 
# Tis is a "generic" file, meaning it van be configured/renamed to 
# support whatever reporting serice is desired.
#
# The primary function used to submit reports is reporting.make().
# This function is required for the mainline to send reporting events to.  This 
# function can then do whatever it needs to send reports to the desired reporting
# service.  The reporting service should be configured in the config.ini file.
#
import logging
import json
import os
import datetime
import urllib3
from email.message import EmailMessage
from configparser import ConfigParser

MODULE_VERSION="statuspage.1.0.0"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.propagate = True
logger.info("%s Module Version %s", __name__, MODULE_VERSION)
logging.getLogger('urllib3').setLevel(logging.WARNING)

import emaillib

try:
    pool = urllib3.PoolManager()
except Exception as e:
    raise Execption from e

#def loadConfiguration(**kwargs):
ini = "statuspage.ini"
logger.debug("Using configuration file = %s", ini)

# verify the file exists
if os.path.exists(ini) is False:
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
            logger.error("cannot add %s.%s.%s = %s", __name__, section_name, name, value)
        # else:
            # logger.debug('%s.%s = %s', section_name, name, value)

logger.debug("Config = %s", config)


def make(**kwargs):
    
    logger.debug("kwargs=%s", kwargs)
    
    alerts=kwargs.get('Alerts', False)
    send = kwargs.get('Send', False)
    status = kwargs.get('Status', 0)
    statusText = kwargs.get('Name', "Not Defined")
    rTime = kwargs.get('Time', 0)
    endpoint = kwargs.get('Endpoint', None)
    url = kwargs.get('Url', None)
    alertConfig=kwargs.get('AlertConfig', None)
    emailConfig = kwargs.get('EmailConfig', None)
    
    if endpoint is None:
        logger.critical("no endpoint in parameters")
        raise ConnectionAbortedError ("no endpoint in parameters")
    
    if config.get('StatusPage').get('apikey') is None:
        logger.critical("no api key in configuration")
        raise ConnectionAbortedError ("no api key in configuration")
    
    if config.get('StatusPage').get('pageids') is None:
        logger.critical("no pageIds in configuration")
        raise ConnectionAbortedError ("no pageIds in configuration")
        
    # check for endpoint in the config
    try:
        componentid = config.get(endpoint)
    except Exception as e:
        logger.error("no statuspage config for %s: %s", endpoint, e)
        raise AttributeError (f"no statuspage config for {endpoint}: {e}")

    try:
        componentid = config.get(endpoint).get('componentid')
    except Exception as e:
        logger.error("no statuspage component for %s: ", endpoint)
        raise AttributeError (f"no statuspage component for {endpoint}: {e}")
    else:
        logger.debug("endpoint = %s config=%s", endpoint, config.get('StatusPage'))
    
    if statusText == "up":
        statusMessage = f"Service is operating as expected. \nReceived {status} (statusText) in {rTime:.3f}ms"
        kwargs['Component'] = componentid
        kwargs['MessageBody'] = statusMessage
        sendUp(**kwargs)
    elif statusText == "down":
        statusMessage = f"Service is not responding to requests."
        kwargs['Component'] = componentid
        kwargs['MessageBody'] = statusMessage
        try:
            sendDown(**kwargs)
        except Exception as e:
            raise ConnectionAbortedError from e
    elif statusText == "degraded":
        statusMessage = f"Service is not responding to requests."
        sendDown(MessageBody=statusMessage, Component=componentid, MailConfig=emailConfig)
    return None

def sendUp(**kwargs):
    """send a message to statuspage indicating the endpoint is up"""
    logger.debug("sending up message")
    messageBody = kwargs.get("MessageBody")
    component = kwargs.get("Component")
    alerts=kwargs.get('Alerts', False)
    send = kwargs.get('Send', False)
    status = kwargs.get('Status', 0)
    statusText = kwargs.get('Name', "Not Defined")
    rTime = kwargs.get('Time', 0)
    endpoint = kwargs.get('Endpoint', None)
    url = kwargs.get('Url', None)
    alertConfig=kwargs.get('AlertConfig', None)
    emailConfig = kwargs.get('EmailConfig', None)

    msg = EmailMessage()
    msg["From"] = emailConfig.get('from')

    msg["Subject"] = "UP"
    msg["To"] = component
    msg.set_content(messageBody)
    kwargs['msg'] = msg
    try:
        emaillib.send(**kwargs)
    except Exception as e:
        logger.error("could not send email: %s", e)
        raise Exception from e

def sendDown(**kwargs):
    """send a message to statuspage indicating the endpoint is down"""
    logger.debug("sending down message")
    
    messageBody = kwargs.get("MessageBody")
    component = kwargs.get("Component")
    alerts=kwargs.get('Alerts', False)
    send = kwargs.get('Send', False)
    status = kwargs.get('Status', 0)
    statusText = kwargs.get('Name', "Not Defined")
    rTime = kwargs.get('Time', 0)
    endpoint = kwargs.get('Endpoint', None)
    url = kwargs.get('Url', None)
    alertConfig=kwargs.get('AlertConfig', None)
    emailConfig = kwargs.get('EmailConfig', None)

    msg = EmailMessage()
    msg["From"] = emailConfig.get('from')
    
    msg["Subject"] = "DOWN"
    msg["To"] = component
    msg.set_content(messageBody)
    kwargs['msg'] = msg
    kwargs['MailTo'] = component
    try:
        emaillib.send(**kwargs)
    except Exception as e:
        logger.error(e)
        raise Exception from e


def sendDegraded(**kwargs):
    """send a message to statuspage indicating the endpoint is degraded"""
    messageBody = kwargs.get("MessageBody")
    mailConfig = kwargs.get("MailConfig")
    component = kwargs.get("Component")
    name = kwargs.get("ComponentName")

    msg = EmailMessage()
    msg["From"] = mailConfig.mailfrom
    try:
        address, domain = component.split("@")
        sendto = f"{address}+degraded_performance@{domain}"
    except Exception as error:
        logging.error("cannot split forTo address: %s", error)
        sendto = component
    msg["Subject"] = "DOWN"
    msg["To"] = sendto
    msg.set_content(messageBody)
    logging.warning("DegradedPerformance Emaiil for %s to %s", name, sendto)
    sendMessage(mailConfig, sendto, msg)


def sendPartialDown(**kwargs):
    """send a message to statuspage indicating the endpoint is partially down"""
    messageBody = kwargs.get("MessageBody")
    mailConfig = kwargs.get("MailConfig")
    component = kwargs.get("Component")

    msg = EmailMessage()
    msg["From"] = mailConfig.mailfrom
    try:
        address, domain = component.split("@")
        sendto = f"{address}+partial_outage@{domain}"
    except Exception as error:
        logging.error("cannot split To address: %s", error)
        sendto = component
    msg["Subject"] = "DOWN"
    msg["To"] = sendto
    msg.set_content(messageBody)
    logging.warning("PartialDown Emaiil to %s", sendto)
    sendMessage(mailConfig, sendto, msg)
    
def getUnresolvedIncidentList(http, EndpointConfig):
    executionStart = datetime.datetime.now()
    response = http.request(
        "GET",
        f"{EndpointConfig.baseUrl}/pages/{EndpointConfig.pageId}/incidents/unresolved",
        headers={"Authorization": f"OAuth {EndpointConfig.apiKey}"},
        retries=EndpointConfig.connectionRetries,
        timeout=EndpointConfig.connectionTimeout,
    )
    result = json.loads(response.data.decode("utf-8"))
    if not result:
        logging.debug("no unresolved incidets")
        raise ValueError("No unresolved incidents")

    if result:
        logging.warning("Current Unresolved Incident Count: %s", len(result))
        for i, incident in enumerate(result):
            logging.debug("Current Incidents: %s", json.dumps(incident, indent=0))

    executionEnd = datetime.datetime.now()
    executionDelta = (executionEnd - executionStart).total_seconds() * 1000
    logging.debug("execution time=%.2fms", executionDelta)
    return result


def getComponentList(http, EndpointConfig):
    """ retrieve the list of components """
    executionStart = datetime.datetime.now()
    response = http.request(
        "GET",
        f"{EndpointConfig.baseUrl}/pages/{EndpointConfig.pageId}/components",
        headers={"Authorization": f"OAuth {EndpointConfig.apiKey}"},
        retries=EndpointConfig.connectionRetries,
        timeout=EndpointConfig.connectionTimeout,
    )

    details = json.loads(response.data.decode("utf-8"))
    logging.debug("component list = %s", json.dumps(details, indent=0))

    executionEnd = datetime.datetime.now()
    executionDelta = (executionEnd - executionStart).total_seconds() * 1000
    logging.debug("execution time=%.2fms", executionDelta)
    return details


# def findIncidentComponentFromComponentList(incidentComponent, componentList):
#     """ find the component detail for an incident component in the component list"""
#     from operator import itemgetter

#     logging.debug("componentList = %s", componentList)
#     logging.debug("want component = %s", incidentComponent)
#     res = map(itemgetter(incidentComponent), componentList)
#     logging.debug("result = %s", res)


def findComponentInIncident(componentId, incidentList):
    from operator import itemgetter

    logging.debug("incidentList = %s", incidentList)
    logging.debug("want component = %s", componentId)
    # res = itemgetter(componentId, incidentList)
    if isinstance(incidentList, list) is not True:
        logging.debug("incident list is not type list()")
        x = incidentList
        incidentList = []
        for i in x:
            incidentList.append(i)
    else:
        logging.debug("incident list is type list()")

    for i, ev in enumerate(incidentList):
        logging.debug("incident id: %s", ev)
        for a, cid in enumerate(ev["components"]):
            logging.debug("component id: %s want: %s", cid["id"], componentId)
            if cid["id"] == componentId:
                logging.debug("matched component id")
                return ev["id"]

    return None

    # logging.info("result = %s", res)


def getIncidentDetails(http, EndpointConfig, incidentId):
    """ dict(incidentDetails) = getIncidentDetails(incidentId)"""

    logging.debug("requesting details for incident %s", incidentId)
    response = http.request(
        "GET",
        f"{EndpointConfig.baseUrl}/pages/{EndpointConfig.pageId}/incidents/{incidentId}",
        headers={"Authorization": f"OAuth {EndpointConfig.apiKey}"},
        retries=EndpointConfig.connectionRetries,
        timeout=EndpointConfig.connectionTimeout,
    )

    result = json.loads(response.data.decode("utf-8"))
    logging.debug("%s", json.dumps(result, indent=0))
    return result


def resolveIncident(**kwargs):

    incidentName = kwargs.get("Name", None)
    deliverNotifications = kwargs.get("Notifications", False)
    autoTransition = kwargs.get("AutoTransition", False)
    incidentMessage = kwargs.get("Message", "Incident resolved")
    componentIds = kwargs.get("ComponentIdList", {})
    components = kwargs.get("Components", {})
    incidentId = kwargs.get("Incident", None)
    baseUrl = kwargs.get("baseUrl", None)
    pageId = kwargs.get("pageId", None)
    apiKey = kwargs.get("apiKey", None)
    http = kwargs.get("PoolManager", None)

    if http is None:
        logging.critical("invalid HTTP PoolManager.")
    return None

    incidentDefinition = {
        "incident": {
            "id": incidentId,
            "name": incidentName,
            "status": "resolved",
            "impact_override": "none",
            "metadata": {},
            "deliver_notifications": deliverNotifications,
            "auto_transition_deliver_notifications_at_end": deliverNotifications,
            "auto_transition_deliver_notifications_at_start": deliverNotifications,
            "auto_transition_to_maintenance_state": autoTransition,
            "auto_transition_to_operational_state": autoTransition,
            "auto_tweet_at_beginning": deliverNotifications,
            "auto_tweet_on_completion": deliverNotifications,
            "auto_tweet_on_creation": deliverNotifications,
            "auto_tweet_one_hour_before": deliverNotifications,
            "body": incidentMessage,
            "components": components,
            "component_ids": componentIds,
        }
    }

    logging.debug("%s", json.dumps(incidentDefinition, indent=0))

    incident = json.dumps(incidentDefinition)
    incident = str(incident)
    incident = incident.encode("utf-8")

    response = http.request(
        "PATCH",
        f"{baseUrl}/pages/{pageId}/incidents/{incidentId}",
        body=incident,
        headers={"Authorization": f"OAuth {apiKey}"},
        retries=EndpointConfig.connectionRetries,
        timeout=EndpointConfig.connectionTimeout,
    )

    return response


def createIncident(**kwargs):

    incidentName = kwargs.get("Name", "Name not Provided")
    deliverNotifications = kwargs.get("Notifications", False)
    autoTransition = kwargs.get("AutoTransition", False)
    incidentMessage = kwargs.get("Message", "Incident created")
    components = kwargs.get("Components", {})
    component_ids = kwargs.get("ComponentIdList", [])
    state = kwargs.get("State", None)
    baseUrl = kwargs.get("baseUrl", None)
    pageId = kwargs.get("pageId", None)
    apiKey = kwargs.get("apiKey", None)
    http = kwargs.get("PoolManager", None)

    if http is None:
        logging.critical("invalid HTTP PoolManager.")
        return None

    if state == "partial_outage":
        impact = "major"
    elif state == "major_outage":
        impact = "critical"
    elif state == "degraded_performance":
        impact = "minor"
    else:
        impact = ""

    incidentDefinition = {
        "incident": {
            "name": incidentName,
            "status": "identified",
            "impact_override": impact,
            "metadata": {},
            "deliver_notifications": deliverNotifications,
            "auto_transition_deliver_notifications_at_end": deliverNotifications,
            "auto_transition_deliver_notifications_at_start": deliverNotifications,
            "auto_transition_to_maintenance_state": autoTransition,
            "auto_transition_to_operational_state": autoTransition,
            "auto_tweet_at_beginning": deliverNotifications,
            "auto_tweet_on_completion": deliverNotifications,
            "auto_tweet_on_creation": deliverNotifications,
            "auto_tweet_one_hour_before": deliverNotifications,
            "body": incidentMessage,
            "components": components,
            "component_ids": component_ids,
        }
    }

    logging.debug("%s", json.dumps(incidentDefinition))

    incident = json.dumps(incidentDefinition)
    incident = str(incident)
    incident = incident.encode("utf-8")

    response = http.request(
        "POST",
        f"{baseUrl}/pages/{pageId}/incidents",
        body=incident,
        headers={"Authorization": f"OAuth {apiKey}"},
        retries=EndpointConfig.connectionRetries,
        timeout=EndpointConfig.connectionTimeout,
    )
    if response.status not in (200, 201):
        logging.warning("createIncident API response status code = %s", response.status)

    return response


def getComponentNameFromId(componentList, componentId):
    """ get the component name from the component id """
    for item in componentList:
        if item["id"] == componentId:
            return item["name"]

    return None


def getComponentIdFromEmail(componentList, componentEmail):
    """ retrieve the component id from the automation email """

    for item in componentList:
        if item["automation_email"] == componentEmail:
            return item["id"]

    return None


def getIncidentComponents(incidentData):

    componentList = []
    logging.debug("%s", incidentData)
    for component in incidentData["components"]:
        logging.debug("adding component %s", component["id"])
        componentList.append(component["id"])

    return componentList


def setIncidentComponentOperationalStatus(incidentData, state):

    componentList = {}

    for component in incidentData["components"]:
        logging.debug("adding component %s", component["id"])
        componentList[component["id"]] = state
    return componentList




