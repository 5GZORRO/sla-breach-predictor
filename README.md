# sla-breach-predictor
SLA Breach Prediction module for 5GZorro

This is a FastApi web service that receives the details of a SLA and starts a training/prediction operation on the metric and threshold given in the parameters. On application startup, the app will try to connect to a Kafka broker specified in the configuration file #properties.conf under the section [kafka]. If the connection fails, a new one can be established later using the REST API.

The app can either be deployed in to ways:

1) As a Kubernetes service using the isbp.yaml file in 'kube files' folder. In this case, the app will automatically connect to the Kafka broker of the Data Lake.
2) As a standalone service for testing purposes. In this case you have to make sure to change the configuration as describe above in order to connect to a local Kafka instance.
