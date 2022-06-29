# Intelligent SLA Breach Predictor

## Introductrion
This is a FastApi web service that receives the details of a SLA and starts a training/prediction operation on the metric and threshold given in the parameters. On application startup, the app will try to connect to a Kafka broker specified in the configuration file properties.conf under the section [kafka]. If the connection fails, a new one can be established later using the REST API.

![ISBP Architecture Components](https://github.com/5GZORRO/sla-breach-predictor/blob/main/ISBP.png?raw=true)

## Prerequisites

#### System Requirements

* **Storage 100 MB**
* **Kubernetes**

Assuming that argo and argo-events are installed in the kubernetes cluster.

1) In order for the app to function as intended, Argo Events must already be present in the cluster.
2) Make sure to install all deployments in the namespace where you installed Argo Events. Be default the yaml files are installed in "argo-events" so if you have a different namespace, change it accordingly.
3) Create a persistentvolume and a persistentvolumeclaim using the volume.yaml file in 'kube files' folder.
4) Lastly, you need to create the Argo resources needed for the workflows to function. file-event.yaml contains the sensor and eventSource. Make sure to create these resources in the same namespace as ISBP.
5) In folder 'kube files' there is a file 'isbp.yaml'. Run it using 'kubectl -n [namespace_name] apply -f isbp.yaml'. This will create an ISBP  deployment and alo a service to expose ISBP to the network as "isbp". Additionally, it will install a MinIO database with a pre-existing "models" bucket to hold zipped ML models. A service for MinIO will also be created.

### Software dependecies

Argo Workflows & Events

### 5GZORRO Module dependencies

Data Lake

## Installation


## Maintainers
**Dimitrios Laskaratos** - *Design & Development* - dlaskaratos@intracom-telecom.com

### REST API 

| Method        | URL           | Use   |
| ------------- |:-------------:| -----:|
| POST      |/service/start|Start a new pipeline. The body must contain the SLA parameters in JSON format. The process is completely automatic given that a topic for reading the monitoring data has been provided. |
| POST      |/add-topic/{topic_name}|Instruct the Kafka consumer to subscribe to a new topic. The topic is added to the list of topics already subscribed to. |
| POST |/service/reconnect  |Force the Kafka consumer and Producer to connect to a broker  |
| DELETE |/service/pipeline/stop/{pipeline_id}| Delete a pipeline  |
| GET |/service/pipeline/{pipeline_id}|Retrieve the details of a pipeline, including the SLA parameters  |
| GET |/get-active-list|Get the list of all active pipelines  |
