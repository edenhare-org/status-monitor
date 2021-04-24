# pylint: disable=C0114
# pylint: disable=C0103
#
# This file defines the parameters for the endpoints to be evaluated
#
__version__="1.0.0"
__author__="chris.hare@icloud.com"
# If at first we don't succeed, re-try once and then consider the endpoint down
connectionRetries = 1
# How long do we wait for a response, in SECONDS
connectionTimeout = 2.0
# How many sequential down checks for a component before we create an incident?
downThreshold = 5
# How many sequential degraded checks for a component before we create an incident?
degradedThreshold = 5
# Statuspage.io
#apiKey = ""
#pageId = ""
#baseUrl = "https://api.statuspage.io/v1"

apiList = [
    {
        "name": "LabR Website",
        "url": "http://www.labr.net",
        "method": "GET",
        "status": 200,
        "timeout": 1000,
        "environment": "prod",
        "region": "us-east-1",
    },
]
