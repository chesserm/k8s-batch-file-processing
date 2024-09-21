import json
import time 

from argparse import ArgumentParser
from kubernetes import client, config
from kubernetes.client.rest import ApiException

MAX_CONCURRENT_JOBS = 10

def submit_job(job_name, image_name, queue_message):
    """
    Submits a job to Kubernetes for processing this file. 

    Inputs:
        - job_name: The name to give the job. **MUST BE UNIQUE WITHIN THE KUBERNETES NAMESPACE**.
        - image_name: The image name to use for the container (must be prebuilt and accessible)
        - queue_message: The queue message to pass to the job as an environment variable.
    
    Outputs:
        - None.
    """
    batch_v1 = client.BatchV1Api()
    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": job_name
        },
        "spec": {
            "backoffLimit": 0, # Don't retry on failure
            "ttlSecondsAfterFinished": 1,  # Automatically delete pod 1 second after completion (default is to not cleanup)
            "parallelism" : 1, # Use only one pod for this job
            "completions" : 1, # Only one successful completion (the one pod) needed for the job to be complete
            "template": {
                "spec": {
                    "containers": [{
                        "name": "my-sample-app",
                        "image": image_name,
                        "imagePullPolicy" : "IfNotPresent",
                        "env": [{
                            "name": "QUEUE_MESSAGE",  # Name of the environment variable
                            "value": queue_message    # Value from the queue message
                        }]
                    }],
                    "restartPolicy": "Never", # Don't retry on failure
                    "imagePullPolicy" : "IfNotPresent"
                }
            }
        }
    }

    try:
        batch_v1.create_namespaced_job(namespace="default", body=job_manifest)
        print(f"Job {job_name} submitted.")
    except ApiException as e:
        print(f"Failed to submit job: {e}")



def get_number_active_jobs(batch_v1):
    """
    Credit: ChatGPT

    Checks the number of active jobs Kubernetes currently has in-progress.

    Inputs:
        - batch_v1: The batch V1 kubernetes API object.
    
    Outputs:
        - num_jobs: The number of active jobs
    """
    try:
        # List all jobs in the 'default' namespace
        jobs = batch_v1.list_namespaced_job(namespace="default")
        
        # Count the number of active jobs
        active_jobs = sum(1 for job in jobs.items if job.status.active)
        
        print(f"Number of active jobs: {active_jobs}")
        return active_jobs

    except Exception as e:
        print(f"Failed to check active jobs: {e}")
        return 0


def main(args):
    """
    Main driver.
    """
    # NOTE: On deployment to AWS Lambda or Azure Function you need the config as part of function files or use secrets.
    config.load_kube_config() 

    # API object from kubernetes
    batch_v1 = client.BatchV1Api()
    
    num_jobs = args.num_jobs
    for i in range(num_jobs):
        while (get_number_active_jobs(batch_v1) >= MAX_CONCURRENT_JOBS):
            print(f"Too many active jobs. Sleeping for 5 seconds...")
            time.sleep(5)

        submit_job(job_name=f"job-{i}",
                    image_name="my-sample-image:latest",
                    queue_message=json.dumps({
                        "id" : f"id_{i}",
                    })
                    )



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--num_jobs", type=int)

    args = parser.parse_args()
    main(args)
