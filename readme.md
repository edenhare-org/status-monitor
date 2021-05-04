# Readme 

This is the source code for the article "Creating a Site Status Monitor using Atlassian StatusPage and AWS CloudWatch" written by Chris Hare and publihsed on Medium.

## What this code Does.

We all want to know the status of our APIs and web sites and how fast they are responding to requests.  This code reads a configuration file with the list of endpoints to query, and saves the results in an AWS CloudWatch metrics namespace.  We can then look at the response over time using the CloudWatch dashboard.  Once we decide if the endpoint is up or down, we will send a message to our Atlassian StatusPage.

## What is in this Repository?

**Check** - a directory with a Python module which does the work of evaluating the target endpoint.
**CloudWatch** - a directory with a Python module that saves the response time data in a CloudWatch metrics namespace.
**endpoints.yaml** - a YAML configuration file with the information on tge endpoints you want to measure.
**monitor.py** - the monitor script.
**StatusPage** - a directory with a Python module that sends a message to StatusPage API a message indicating if the endpoint is up or down.

## The endpoints.yaml configuration file

Here is an example configuration file:

```
# set the applicton configuration
monitor:
  # how long to delay between connection attempts.  See this 
  # value to 0 (zero) to evaluate the endpoints once.  This is 
  # one way to use the same code for AWS Lambda or as a service
  # in AWS Elastic Container Service.
  delay: 60
  # the loglevel.  Leave this blank or remove the line to leave
  # the logging level set to the default of 'INFO'
  loglevel:

connection:
  # This section sets the urllib3 request configuration.
  retries: 1
  # How long do we wait for a response, in SECONDS
  timeout: 2.0
    
statuspage:
  # Statuspage.io api key
  apiKey: 
  # This example assumes you only have one page in your StatusPage
  # account. If you have multiple pages, like a public ad a private
  # page, adding the componentid and the pageid to the api/endpoint
  # section would be a good idea.
  pageId: 
  # URL for the API endpoint
  baseUrl: "https://api.statuspage.io/v1"
  # how many sequential failures before we conclude the endpoint is
  # offline
  downThreshold: 5
  # how many sequential reauests with a valid response which is
  # greaster than the target response time before we send a 
  # degraded_performance status
  degradedThreshold: 5
    
cloudwatch:
  # Set this value to save the metrics to Cloudwatch.  If this
  # value is null, then no metrics are saved to CloudWatch metrics.
  namespace: 

apiList:
  # This is a list of the endpoints/APIs we want to test.
  - name: endpoint descriptive name
    url: http://www.google.com
    method: "GET"
    # the expected response code
    status: 200
    # The time we expected a res
    timeout: 1000
    # change the log level only for this connection.  Remove this or
    # set to blank to use the same log level as defined in the 
    # monitor section above.
    loglevel: INFO
    # StatusPage component id.  This is used to update the operational
    # status usinjg the API or through email automation by using the 
    # API to look up the component email.
    componentid: 
```

## Running the monitor script

The script has several options:
  -f, --file; specify an alternate configuration file than endpoints.yaml;
  -l, -- log; specify an alternate log file than monitor.log;
  -v, --version; print the version details;
  -r, --runonce; evaluate all of the endpoints in the configuration file and exit.
  
If no options are specified and the command is executed in a shell, the log records are written on the terminal console.  If a log file is specified on the command line, then the log records are written to the file.

```
$ python3 monitor.py --runonce
INFO:root:__main__ Module Version 1.0.22/labrlearning.medium.com
INFO:root:Initializing loop
WARNING:root:cloudwatch metrics disabled by configuration
endpoint: http://www.labr.net status: 2xx (200) time: 256.16ms metrics: disabled 
INFO:root:endpoint: http://www.labr.net status: 2xx(200) time: 256.1624460213352 ms metrics: None(None)
INFO:root:execution complete
execution complete.
```

## Bugs and Suggestions
If you have comments, suggestions or feedback, please open an issue.