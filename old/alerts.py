import logging
import json
import datetime
import importlib
import boto3
from email.message import EmailMessage
    
MODULE_VERSION="1.0.0"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

logger.info("%s Module Version %s", __name__, MODULE_VERSION)
logging.getLogger('boto3').setLevel(logging.WARNING)

try:
    import emaillib as mail
except Exception as e:
    logger.critical("failed to import emaillib")
    raise ImportError from e


snsClient = boto3.client('sns')

def notify(**kwargs):

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

    # check the alert configuration
    if alertConfig is None:
        raise AttributeError ("no alert configuration provided")
    
    # verify we got a configuration dict to send email.
    if emailConfig is None:
        raise AttributeError ("no email configuration provided")
    
    # if we are supposed to notify some other service, import it.
    # reporting services are 
    #    Atlassian StatusPage
    #! Note: the reporting module must provide a function named 'make'
    if alertConfig.get('reporting', None) is not None:
        # This is a dynamic import
        try:
            reporting = importlib.import_module(alertConfig.get('reporting'))
        except Exception as e:
            logger.warning('no status page reporting module: %s', e)
    else:
        reporting = None

    # Send a notification.  The notifications are sent to the SNS topic 
    # and email address defined in the 'alerts' section of the config.ini 
    # file
    if alerts is True and send is True:
        logger.debug("send notification")
        try:
            sendSns(**kwargs)
        except Exception as e:
            logger.critical()("could not send SNS notification: %s", e)
            # raise Exception from e
        try:
            msg = EmailMessage()
            msg["From"] = emailConfig.get('from')
            msg["Subject"] = f"{endpoint} is {statusText}"
            msg["To"] = alertConfig.get('email', None)
            Message=f"Endpoint {endpoint} is {statusText}"
            msg.set_content(Message)
            kwargs['Message'] = msg
            kwargs['MailTo'] = alertConfig.get('email', None)
            mail.send(**kwargs)
        except Exception as e:
            logger.error("could not send email: %s", e)
        try:
            reporting.make(**kwargs)
        except Exception as e:
            logger.error("could not send notification: %s", e)
    elif alerts is True and send is False:
        logger.debug("OK - no notification required")
        if statusText is "up":
            logger.info("Endpoint: %s at %s is %s (%s) in %.3fms",
                endpoint, url, statusText, status, rTime)
        else:
            logger.warning("Endpoint: %s at %s is %s (%s) in %.3fms",
                endpoint, url, statusText, status, rTime)
    elif alerts is False and send is True:
        logger.warning("endpoint offline, alerts are disabled")
        logger.warning("Endpoint: %s at %s is %s (%s) in %.3fms",
            endpoint, url, statusText, status, rTime)
    elif alerts is False:
        logger.info("alerting disabled by configuration")
        return None
    
    return None
    
def sendSns(**kwargs):
    
    # logger.debug(kwargs)
    
    alerts=kwargs.get('Alerts', False)
    send = kwargs.get('Send', False)
    status = kwargs.get('Status', 0)
    statusText = kwargs.get('Name', "Not Defined")
    rTime = kwargs.get('Time', 0)
    endpoint = kwargs.get('Endpoint', None)
    url = kwargs.get('Url', None)
    alertConfig=kwargs.get('AlertConfig', None)
    emailConfig = kwargs.get('EmailConfig', None)
    
    if alertConfig.get('sns') is None:
        raise AttributeError ("No topic defined. Notificatiion not sent.")
    
    logger.debug("topic: %s", alertConfig.get('sns'))
    
    try:
        response = snsClient.publish(
            TopicArn=alertConfig.get('sns'),
            Message=f"Endpoint {endpoint} is {statusText}",
            Subject=f'Service {statusText}'
            )
    #    MessageStructure='string',
    #    MessageAttributes={
    #        'string': {
    #            'DataType': 'string',
    #            'StringValue': 'string',
    #            'BinaryValue': b'bytes'
    #        }
    #    },
    #    MessageDeduplicationId='string',
    #    MessageGroupId='string'
    #)
    except Exception as e:
        raise Exception from e
    else:
        logger.info('SNS Notification sent: %s', response.get('MessageId')) 

    return None
    

#def sendEmail(**kwargs):
#    
#    #logger.debug(kwargs)
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
#    if emailConfig.get('server') is None:
#        raise AttributeError ("No SMTP/Email server defined. Notificatiion not sent.")
#    
#    return None
#    


#def sendMessage(Mail, sendto, msg):
#    """sendMessage
#
#    Args:
#        Mail (dict): Mail server configuration
#        sendto (list): Email addresses to send the notification to
#        msg (str): the message text
#    """
#    try:
#        with smtplib.SMTP(Mail.server, Mail.port) as server:
#            try:
#                server.starttls()  # Secure the connection
#            except Exception as error:
#                logging.critical(
#                    "Could not initialize TLS SMTP connection %s:%s: %s",
#                    Mail.server,
#                    Mail.port,
#                    error,
#                )
#                return
#            try:
#                server.login(Mail.username, Mail.password)
#            except Exception as error:
#                logging.critical(
#                    "Could not initialize TLS SMTP connection %s:%s: %s",
#                    Mail.server,
#                    Mail.port,
#                    error,
#                )
#                return
#            try:
#                server.sendmail(Mail.mailfrom, [sendto], msg.as_string())
#            except Exception as error:
#                logging.error("type error: %s", type(error))
#                logging.error("cannot send email: %s", error)
#            else:
#                logging.debug("Successfully sent email")
#                logging.debug("to: %s msg: %s", sendto, msg)
#    except Exception as error:
#        logging.critical(
#            "could not initialize SMTP connection %s:%s: %s",
#            Mail.server,
#            Mail.port,
#            error,
#        )
#
#    return
#

