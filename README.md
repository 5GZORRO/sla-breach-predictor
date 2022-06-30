# Intelligent SLA Breach Predictor

## Introductrion
This is a FastApi web service that receives the details of a SLA and starts a training/prediction operation on the metric and threshold given in the parameters. The main module (ISBP) requests predictions from the Predictor service every time that 'X' metrics are received. After every prediction, the next monitoring metric is used to assess the accuracy of that prediction. If the average of 'Y' such assessments is found to be lower than  a pre-configured threshold (eg. 98%), a training job for that specific SLA and model is ordered. An ML model for the forecasts is selected from a pool of models that are pre-trained on that particular metric.

![ISBP Architecture Components](https://github.com/5GZORRO/sla-breach-predictor/blob/main/ISBP.png?raw=true)

## Prerequisites

#### System Requirements
* **Storage 100 MB**
* **Kubernetes**

### Software dependecies
Argo Workflows & Events

### 5GZORRO Module dependencies
Data Lake

## Installation

Assuming that argo and argo-events are installed in the kubernetes cluster.

1) In order for the app to function as intended, Argo Events must already be present in the cluster.
2) Make sure to install all deployments in the namespace where you installed Argo Events. Be default the yaml files are installed in "argo-events" so if you have a different namespace, change it accordingly.
3) Create a persistentvolume and a persistentvolumeclaim using the volume.yaml file in 'kube files' folder.
4) Lastly, you need to create the Argo resources needed for the workflows to function. file-event.yaml contains the sensor and eventSource. Make sure to create these resources in the same namespace as ISBP.
5) In folder 'kube files' there is a file 'isbp.yaml'. Run it using 'kubectl -n [namespace_name] apply -f isbp.yaml'. 
    * This will create an ISBP  deployment and alo a service to expose ISBP to the network as "isbp".
    * It will install a MinIO database with a pre-existing "models" bucket to hold zipped ML models. A service for MinIO will also be created.
    * It will create a Predictor web service deployment and expose it as "predictor".

### Docker installation
N/A

## Configuration
A configuration file 'properties.conf' is located in the root folder of ISBP. It specifies :
  *  the Kafka queue to connect to (includng the topic).
  *  the number of data points to use for model re-training
  *  the data points for the calculation of average accuracy
  *  the number of predictions in order to select a ML model
  *  the accuracy threshold that all models must adhere to.
 
NOTE: When changing this configuration file, the image must be built again and restart the system on Kubernetes for the changes to take effect.

## Maintainers
**Dimitrios Laskaratos** - *Design & Development* - dlaskaratos@intracom-telecom.com

## License
This module is distributed under Apache License 2.0
