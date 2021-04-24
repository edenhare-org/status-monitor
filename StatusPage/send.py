import logging
__version__="1.0.0"
__author__="chris.hare@icloud.com"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.info("%s Module Version %s/%s", __name__, __version__, __author__)


def status(**kwargs):
    """use the update_component api to indicate the endpoint is operational"""
    
    logger.debug("kwargs = %s", kwargs)
    
    if kwargs.get('Status') not in ("operational", "under_maintenance", "degraded_performance", "partial_outage", "major_outage"):
        logger.error("invalid status: %s", kwargs.get('Status'))
        raise ValueError("invalid status")
#    
#    {
#  "component": {
#    "description": "string",
#    "status": "operational",
#    "name": "string",
#    "only_show_if_degraded": true,
#    "group_id": "string",
#    "showcase": true,
#    "start_date": "2021-04-24"
#  }
#}
#
#    logger.debug("sending up message")
#    messageBody = kwargs.get("MessageBody")
#    component = kwargs.get("Component")
#    alerts=kwargs.get('Alerts', False)
#    send = kwargs.get('Send', False)
#    status = kwargs.get('Status', 0)
#    statusText = kwargs.get('Name', "Not Defined")
#    rTime = kwargs.get('Time', 0)
#    endpoint = kwargs.get('Endpoint', None)
#    url = kwargs.get('Url', None)
#    alertConfig=kwargs.get('AlertConfig', None)
#    emailConfig = kwargs.get('EmailConfig', None)
#
#    msg = EmailMessage()
#    msg["From"] = emailConfig.get('from')
#
#    msg["Subject"] = "UP"
#    msg["To"] = component
#    msg.set_content(messageBody)
#    kwargs['Message'] = msg
#    kwargs['MailTo'] = component
#    try:
#        emaillib.send(**kwargs)
#    except Exception as e:
#        logger.error("could not send email: %s", e)
#        raise Exception from e
#

