def handler(event, context):
    url = os.environ.get('URL', "http://www.labr.net")
    loglevel = os.environ.get('LOGLEVEL', 'DEBUG')
    logger.setLevel(loglevel)
    logger.info("loglevel = %s", logging.getLevelName(logger.level))
    
    if url is None:
        logger.error("url not specified")
        print("No url was provided")
        return {
            'statusCode': 400,
            'body': "ERROR",
            'url': url,
            'error': "no url was provided/found in the environment.",
        }
    
    #! The code doesn't know how to handle POST
    method = os.environ.get('METHOD', 'GET')
    timeout = os.environ.get('TIMEOUT', 3)
    retries = os.environ.get('RETRIES', 3)

    #! The code doesn't know how to handle these yet
    body = os.environ.get('BODY', None)
    headers = os.environ.get('HEADERS', None)
    auth = os.environ.get('AUTH', None)
    # These environment variables control posting to Atlassian StatusPage
    reporting = os.environ.get('REPORT', True)
    componentId = os.environ.get('COMPONENT', "test")
    pageId = os.environ.get('PAGEID', "j0wsqcqrh6y4")
    componentName = os.environ.get('CNAME', None)
    baseUrl = os.environ.get('BASEURL', "https://api.statuspage.io/v1")
    apiKey = os.environ.get('APKIKEY', "98940f25-5813-41f2-bce6-cfdcbfd251dc")
    
    #
    # Check to see if componentId is a comma separated string/list.  This 
    # allows one endpoint to be on multiple pages such as a public and a 
    # private page.  It will have different componentIds.
    # 
    if componentId is not None and pageId is not None and reporting is True:
        # convert to a list
        componentId = componentId.split(',')
        print(componentId)
        # convert to a list
        pageId = pageId.split(',')
        print(pageId)

        componentList = StatusPage.getComponentList(BaseUrl=baseUrl,
                        PageIds=pageId,
                        ApiKey=apiKey,
                        Retries=retries,
                        Timeout=timeout)
        print(componentList)

        if len(componentId) != len(pageId):
            # maybe this should try to find the component id before 
            # failing, provided reporting is True.
            
            return {
                'statusCode': 500,
                'body': "ERROR",
                'url': url,
                'error': "CompnentId and PageId have different lengths.  If providing a componentId and pageId, they must have the same number of comma separated items.",
            }
    elif componentId is None and pageId is not None:
        logger.warning("both componentId and pageId values must be provided")
        reporting = False
    elif componentId is not None and pageId is None:
        logger.warning("both componentId and pageId values must be provided")
        reporting = False   
    else:
        logger.info("reporting has been disabled due to provided configuration")
        reporting = False   
        
    event = {
        'url': url,
        'method': method,
        'timeout': timeout,
        'retries': retries,
        'loglevel': loglevel,
        'body': body,
        'headers': headers,
        'auth': auth,
        'componentId': componentId,
        'pageId': pageId
    }
    
    response = Check.status(event, '')
    cw_response = CloudWatch.put(response, '')
    
    
    return cw_response
