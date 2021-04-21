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

incidents = {}
# structure
# incidents = {
#    id = componentid,
#    incident = incidentid
#    created = creation date
# }

components = []

def make(**kwargs):
#    
#    global components
#    
#    if not components:
#        components = getComponentList()
#        

    #logger.debug("kwargs=%s", kwargs)
    
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
        #logger.error("no statuspage config for %s: %s", endpoint, e)
        raise AttributeError (f"no statuspage config for {endpoint}")

    try:
        componentid = config.get(endpoint).get('componentid')
    except Exception as e:
        #logger.error("no statuspage component for %s: ", endpoint)
        raise AttributeError (f"no statuspage component id for {endpoint}")
    else:
        logger.debug("endpoint = %s config=%s", endpoint, config.get('StatusPage'))
    
    address, domain = componentid.split("@")
    logger.debug("address = %s domain = %s", address, domain)
            
    try:
        openIncidents = getUnresolvedIncidentList()
    except Exception as e:
        logger.error("cannot get open incidents: %s", e)
    else:
        logger.debug("open incidents = %s", openIncidents)
    # is this component in an open incident?
    activeIncident = findComponentInIncident(address, openIncidents)
    logger.debug("activeIncident = %s", activeIncident)
    
    if statusText == "up":
        statusMessage = f"Service is operating as expected. \nReceived {status} (statusText) in {rTime:.3f}ms"
        kwargs['Component'] = componentid
        kwargs['MessageBody'] = statusMessage
        sendUp(**kwargs)
        # check for an incident.
        # if an incident with [AUTO] in the title, close it.
    elif statusText == "down":
        statusMessage = f"Service is not responding to requests."
        kwargs['Component'] = componentid
        kwargs['MessageBody'] = statusMessage
        try:
            sendDown(**kwargs)
        except Exception as e:
            raise ConnectionAbortedError from e
        # check for an incident
        # if no incident, then create one
        logger.debug("requesting incident creation")
        try:
            response = createIncident(
                Name="[AUTO] new incident",
                Message=f"Incident created: {statusMessage}",
                Components={
                    address: "major_outage",
                    },
                ComponentIdList=[address],
                State="major_outage"
            )
        except Exception as e:
            logger.error("cannot create incident: %s", e)
        else:
            logger.debug("created incident: %s", response)
    elif statusText == "degraded":
        statusMessage = f"Service is not responding to requests."
        sendDown(MessageBody=statusMessage, Component=componentid, MailConfig=emailConfig)
    return None

def updateConfig(config):
    
    # This module takes the provided configuration file and tries to insert
    # the component details
    
    logger.debug("provided config = %s", config)
    
    try:
        components = getComponentList()
    except Exception as e:
        logger.error("cannot retrieve component list: %s", e)    
        raise ValueError ("cannot retrieve component list") from e
    
    for a, details in enumerate(components):
        # look for the name of this component in the Sections of the
        # config.ini
        logger.debug("details = %s", details)
        if details.get('name') in config:
            logger.debug("found %s", details.get('name'))
    
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
    kwargs['Message'] = msg
    kwargs['MailTo'] = component
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
    kwargs['Message'] = msg
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
        logger.error("cannot split forTo address: %s", error)
        sendto = component
    msg["Subject"] = "DOWN"
    msg["To"] = sendto
    msg.set_content(messageBody)
    logger.warning("DegradedPerformance Emaiil for %s to %s", name, sendto)
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
        logger.error("cannot split To address: %s", error)
        sendto = component
    msg["Subject"] = "DOWN"
    msg["To"] = sendto
    msg.set_content(messageBody)
    logger.warning("PartialDown Emaiil to %s", sendto)
    sendMessage(mailConfig, sendto, msg)
    
def getUnresolvedIncidentList():

    try:
        response = pool.request(
            "GET",
            f"{config.get('StatusPage').get('api',None)}/pages/{config.get('StatusPage').get('pageids',None)}/incidents/unresolved",
            headers={
                "Authorization": f"OAuth {config.get('StatusPage').get('apikey')}"
                },
            retries=config.get('StatusPage').get('retries',3),
            timeout=int(config.get('StatusPage').get('timeout',3))
        )
    except Exception as e:
        logger.error("cannot retrieve open incidents: %s", e)
        raise ConnectionAbortedError from e
    
    result = json.loads(response.data.decode("utf-8"))
    logger.debug("result = %s", result)
    
    if not result:
        logger.debug("no unresolved incidets")
    else:
        logger.warning("Current Unresolved Incident Count: %s", len(result))
        for i, incident in enumerate(result):
            logger.debug("Current Incidents: %s", json.dumps(incident, indent=0))

    return result


def getComponentList():
    """ retrieve the list of components """

    response = pool.request(
        "GET",
        f"{config.get('StatusPage').get('api', None)}/pages/{config.get('StatusPage').get('pageids')}/components",
        headers={"Authorization": f"OAuth {config.get('StatusPage').get('apikey', None)}"},
        retries=config.get('StatusPage').get('retries',3),
        timeout=int(config.get('StatusPage').get('timeout',3))
    )

    details = json.loads(response.data.decode("utf-8"))
    logger.debug("component list = %s", json.dumps(details, indent=0))

    return details


# def findIncidentComponentFromComponentList(incidentComponent, componentList):
#     """ find the component detail for an incident component in the component list"""
#     from operator import itemgetter

#     logger.debug("componentList = %s", componentList)
#     logger.debug("want component = %s", incidentComponent)
#     res = map(itemgetter(incidentComponent), componentList)
#     logger.debug("result = %s", res)


def findComponentInIncident(componentId, incidentList):
    from operator import itemgetter

    logger.debug("incidentList = %s", incidentList)
    logger.debug("want component = %s", componentId)
    # res = itemgetter(componentId, incidentList)
    if isinstance(incidentList, list) is not True:
        logger.debug("incident list is not type list()")
        x = incidentList
        incidentList = []
        for i in x:
            incidentList.append(i)
    else:
        logger.debug("incident list is type list()")

    for i, ev in enumerate(incidentList):
        logger.debug("incident id: %s", ev)
        for a, cid in enumerate(ev["components"]):
            logger.debug("component id: %s want: %s", cid["id"], componentId)
            if cid["id"] == componentId:
                logger.debug("matched component id")
                return ev["id"]

    return None

    # logger.info("result = %s", res)


def getIncidentDetails(http, EndpointConfig, incidentId):
    """ dict(incidentDetails) = getIncidentDetails(incidentId)"""

    logger.debug("requesting details for incident %s", incidentId)
    response = http.request(
        "GET",
        f"{EndpointConfig.baseUrl}/pages/{EndpointConfig.pageId}/incidents/{incidentId}",
        headers={"Authorization": f"OAuth {EndpointConfig.apiKey}"},
        retries=EndpointConfig.connectionRetries,
        timeout=EndpointConfig.connectionTimeout,
    )

    result = json.loads(response.data.decode("utf-8"))
    logger.debug("%s", json.dumps(result, indent=0))
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
        logger.critical("invalid HTTP PoolManager.")
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

    logger.debug("%s", json.dumps(incidentDefinition, indent=0))

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

    logger.debug(kwargs)
    
    incidentName = kwargs.get("Name", "Name not Provided")
    deliverNotifications = kwargs.get("Notifications", False)
    autoTransition = kwargs.get("AutoTransition", True)
    incidentMessage = kwargs.get("Message", "Incident created")
    components = kwargs.get("Components", {})
    component_ids = kwargs.get("ComponentIdList", [])
    state = kwargs.get("State", None)
    
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

    logger.debug("%s", incidentDefinition)

    incident = json.dumps(incidentDefinition)
    incident = str(incident)
    incident = incident.encode("utf-8")

    try:
        response = pool.request(
            "POST",
            f"{config.get('StatusPage').get('api', None)}/pages/{config.get('StatusPage').get('pageids')}/incidents",
            body=incident,
            headers={"Authorization": f"OAuth {config.get('StatusPage').get('apikey')}"},
            retries=config.get('StatusPage').get('retries',3),
            timeout=int(config.get('StatusPage').get('timeout',3))
        )
    except Exception as e:
        logger.error("cannot create incident: %s", e)
        
    if response.status not in (200, 201):
        logger.error("createIncident API response status code = %s", response.status)
        logger.error("response: %s", json.loads(response.data.decode("utf-8")))

    return json.loads(response.data.decode("utf-8"))


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
    logger.debug("%s", incidentData)
    for component in incidentData["components"]:
        logger.debug("adding component %s", component["id"])
        componentList.append(component["id"])

    return componentList


def setIncidentComponentOperationalStatus(incidentData, state):

    componentList = {}

    for component in incidentData["components"]:
        logger.debug("adding component %s", component["id"])
        componentList[component["id"]] = state
    return componentList




