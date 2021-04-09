# sla-breach-predictor
SLA Breach Prediction module for 5GZorro

This is a FastApi web service that receives the details of a SLA and starts a training/prediction operation on the metric and threshold given in the request parameters.

For now, there are two ways to run the service:

1) As a standalone service. In this case you need to have several python packages installed (the complete list can be found in the Dockerfile here: 5gzorroApp/python image/) which can be time consuming.
2) As a docker microservice using "docker-compose up" in the root folder. This will install all required python packages, although the base image might take some time to be created. On startup, the service will try to connect to a Kafka service so make sure you have one set up and, most importantly, provide the host and port in the configuration file "poperties.conf" located in the root folder. 

If you intend to start a prediction pipeline, you also need to provide in the configuration file the topic from which the consumer will read monitoring data, and also the topic to which the producer will send the notifications.

# SLA Format

The service currently accepts the following format for an SLA:

{
    "id" : 123,
    "_name" : "abcd",
    "description" : "This is abcd sla",
    "_rules" : [
            {
                "metric" : "bandwidth",
                "tolerance" : 2600,
                "model_data" : {
                    "base" : "lstm",
                    "spec" : "univariate",
                    "n_steps" : 3,
                    "out" : 1
                }
            }
    ]
}

This format will most likely change depending on the needs of the datalake.

Additionally, the monitoring data must have the following format:

{
"[your_metric]" : [the value],
"[time]" : [a UNIX timestamp]
}

The monitoring data format is also subject to change.
