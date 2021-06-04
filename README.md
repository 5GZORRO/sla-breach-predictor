### sla-breach-predictor
SLA Breach Prediction module for 5GZorro

This is a FastApi web service that receives the details of a SLA and starts a training/prediction operation on the metric and threshold given in the parameters. On application startup, the app will try to connect to a Kafka broker specified in the configuration file properties.conf under the section [kafka]. If the connection fails, a new one can be established later using the REST API.

# HOW TO DEPLOY

# REST API

URL: isbp:8000

# POST /service/start
Start a new pipeline. The body must contain the SLA parameters in JSON format. The process is completely automatic given that a topic for reading the monitoring data has been provided.

# 

| Method        | URL           | Use   |
| ------------- |:-------------:| -----:|
| POST      | /service/start | Start a new pipeline. The body must contain the SLA parameters in JSON format. The process is completely automatic given that a topic for reading the monitoring data has been provided. |
| col 2 is      | centered      |   $12 |
| zebra stripes | are neat      |    $1 |
