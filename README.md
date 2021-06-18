# sla-breach-predictor
SLA Breach Prediction module for 5GZorro

This is a FastApi web service that receives the details of a SLA and starts a training/prediction operation on the metric and threshold given in the parameters. On application startup, the app will try to connect to a Kafka broker specified in the configuration file properties.conf under the section [kafka]. If the connection fails, a new one can be established later using the REST API.

### HOW TO DEPLOY

Assuming that argo and argo-events are installed in the kubernetes cluster.

1) Create a persistentvolume and a persistentvolumeclaim using the volume.yaml file in 'kube files' folder. WARNING: tha yaml file creates the volume on a multi-node cluster, which is why path and nodeAffinity are taken into account. Make sure to change the values accordingly when deploying on your own cluster. Additionally, in order for every pod to successfully mount the volume, taints and tolerations must also be accounted for. For more information : https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ .
2) In folder 'kube files' there is a file 'isbp.yaml'. Run it using 'kubectl -n [namespace_name] apply -f isbp.yaml'. This will create a deployment and alo a service to expose ISBP to the network as "isbp".
3) Lastly, you need to create the Argo resources needed for the workflows to function. file-event.yaml contains the sensor and eventSource. Make sure to create these resources in the same namespace as ISBP.

### REST API 

| Method        | URL           | Use   |
| ------------- |:-------------:| -----:|
| POST      |/service/start|Start a new pipeline. The body must contain the SLA parameters in JSON format. The process is completely automatic given that a topic for reading the monitoring data has been provided. |
| POST      |/add-topic/{topic_name}|Instruct the Kafka consumer to subscribe to a new topic. The topic is added to the list of topics already subscribed to. |
| POST |/service/reconnect  |Force the Kafka consumer and Producer to connect to a broker  |
| DELETE |/service/pipeline/stop/{pipeline_id}| Delete a pipeline  |
| GET |/service/pipeline/{pipeline_id}|Retrieve the details of a pipeline, including the SLA parameters  |
| GET |/get-active-list|Get the list of all active pipelines  |
