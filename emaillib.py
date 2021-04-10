import logging
import json
import datetime
import smtplib

MODULE_VERSION="1.0.0"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

logger.info("%s Module Version %s", __name__, MODULE_VERSION)


def send(**kwargs):
    
    logger.debug(kwargs)
    
    alerts=kwargs.get('Alerts', False)
    send = kwargs.get('Send', False)
    status = kwargs.get('Status', 0)
    statusText = kwargs.get('Name', "Not Defined")
    rTime = kwargs.get('Time', 0)
    endpoint = kwargs.get('Endpoint', None)
    url = kwargs.get('Url', 'Not Defined')
    msg = kwargs.get('Message','No message specified.')
    alertConfig=kwargs.get('AlertConfig', None)
    emailConfig = kwargs.get('EmailConfig', None)
    sendto = kwargs.get('MailTo', None)
    
    if alerts is False or send is False:
        raise AttributeError ("alert or send is False. Notification not sent.")
    
    if endpoint is None:
        raise AttributeError ("no endpoint defined. Notification not sent.")

    if sendto is None:
        raise AttributeError ("no send address defined. Notification not sent.")
            
    if emailConfig is None:
        raise AttributeError ("No mail configuration defined. Notification not sent.")
    
    if alertConfig is None:
        raise AttributeError ("No alert configuration defined. Notification not sent.")
    
    if emailConfig.get('server') is None:
        raise AttributeError ("No SMTP/Email server defined. Notification not sent.")
    
    try:
        server = smtplib.SMTP(emailConfig.get('server'),
            emailConfig.get('port'))
    except Exception as error:
        logging.critical(
            "could not initialize SMTP connection %s:%s: %s",
            emailConfig.get('server'),
            emailConfig.get('port'),
            error
        )
        raise ConnectionAbortedError from error
        
    try:
        server.starttls()  # Secure the connection
    except Exception as error:
        logging.critical(
            "Could not initialize TLS SMTP connection %s:%s: %s",
            emailConfig.get('server'),
            emailConfig.get('port'),
            error
        )
        raise ConnectionAbortedError from error
        
    try:
        server.login(emailConfig.get('authuser'), emailConfig.get('authpass'))
    except Exception as error:
        logging.critical(
            "Could not initialize TLS SMTP connection %s:%s: %s",
            emailConfig.get('server'),
            emailConfig.get('port'),
            error
        )
        raise ConnectionAbortedError from error
    
    try:
        server.sendmail(emailConfig.get('from'), [sendto], msg.as_string())
    except Exception as error:
        logging.error("type error: %s", type(error))
        logging.error("cannot send email: %s", error)
        raise ConnectionRefusedError from error
    else:
        logging.debug("Successfully sent email")
        logging.debug("to: %s msg: %s", sendto, msg)
                
    return None

