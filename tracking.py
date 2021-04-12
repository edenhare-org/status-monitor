import logging
import json
import datetime

MODULE_VERSION="1.0.0"
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

logger.info("%s Module Version %s", __name__, MODULE_VERSION)

# structure is
# history: {
#   endpoint: {
#     state: up|down|degraded
#     counter: int
#     timer: float
#     time: utc_timestamp
#     alerts: int
#     last_alert = utc_timestamp
#   }   
# }
history = {}

def save(**kwargs):
    
    global history
    
    logger.debug(kwargs)
    
    endpoint = kwargs.get('Endpoint', None)
    state = kwargs.get('State', "up")
    rtime = kwargs.get('ResponseTime', 0)
    lastCheck = kwargs.get('CheckTime', None)
    downthreshold = kwargs.get('Down', 0)
    degradedthreshold = kwargs.get('Degraded', 0)
    alertfrequency = kwargs.get('AlertFrequency',5)
    
    # if we don't have an endpoint, raise an error
    if endpoint is None:
        raise AttributeError ("no endpoint provided")
    
    logger.debug('history type = %s', type(history))
 
    logger.debug('history = %s', history)
    #try:
    if endpoint not in history:
        history[endpoint] = {}
    data = history.get(endpoint)

    # get the last state. 
    logger.debug('data type = %s', type(data)) 
    try:
        lastState = data.get('state')
    except Exception as e:
        logger.debug("%s", e)
        data['state'] = state
        lastState = state

    if lastState != state:    
        data['state'] = state
    
    counter = data.get('counter',5)
    timer = data.get('timer', 0)
    alerts = data.get('alerts', 0)
    if state == "down" or state == "degraded":
        history[endpoint]['counter'] = counter + 1
    elif state == "up":
        history[endpoint]['counter'] = 0

    
    if int(data.get('counter')) > int(downthreshold) and \
        int(data.get('counter')) % int(alertfrequency) == 0:
        alert = True
        alertType = "count"
    elif int(rtime) > int(degradedthreshold) and \
        int(data.get('counter')) > int(downthreshold) and \
        int(data.get('counter')) % int(alertfrequency) == 0:
        alert = True
        alertType = "time"
    elif lastState != state:
        alert = True
        alertType = "reset"
    else:
        alert = False
        alertType = None 

    # Save the state
    data['timer'] = rtime
    logger.debug(history)
    return {
        'alert': alert,
        'type': alertType
    }


