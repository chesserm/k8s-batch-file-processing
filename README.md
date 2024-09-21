# Exploring Kubernetes for Batch File Processing

This repo explores using kubernetes to facilitate batch processing of files. 

The code is setup to run locally. All development + testing was done using: 
- Docker Desktop
- WSL 2 (Ubuntu 22.0.4.5 LTS)
- minikube + kubectl

## Functionality

Kubernetes will receive jobs and simulate processing a file. This is setup to simulate each individual job processing one file and for each job to run on a single (dedicated) pod (container). 

The driver script `send_request.py` is meant to simulate an AWS Lambda or Azure Function which pulls messages off of a queue and send these messages to kubernetes for batch processing. 

To avoid kubernetes horizontally scaling infinitely, the driver script checks the number of running jobs and will only submit a new job if the number of running jobs is less than a specified constant variable `MAX_CONCURRENT_JOBS`. If the number of jobs is equal to `MAX_CONCURRENT_JOBS`, the script sleeps for 5 seconds before checking again.


## Usage

1. Ensure Docker Desktop is running
2. Start kubernetes (minikube) via `minikube start`
3. Run the following to ensure you are on the same docker-env as minikube: `eval $(minikue docker-env)`
4. Build the image: `cd k8s && docker-compose build`
5. Ensure that `my-sample-image` is shown in the output of running the command `docker images`
6. (Optional) Run the kubernetes dashboard to monitor the submission to jobs
7. (Recommended) Change the value for `ttlSecondsAfterFinished` in the JSON request made by `submit_job()` in `send_request.py` to avoid kubernetes cleaning up pods immediately after they complete
8. Run the following to submit jobs to kubernetes: `cd .. && python3 send_request.py -n 25`
    - The `--num_jobs` flag is how many jobs to submit. Within `send_request.py` you have a `MAX_CONCURRENT_JOBS` param to adjust as desired.

If you attempt to run the command multiple times, you will get an error that the job already exists, you can clean up jobs with: `kubectl delete jobs --all` to fix this. Likewise, if you change the `ttlSecondsAfterFinished` parameter (or remove it entirely), you can cleanup pods with: `kubectl delete pods --all`.

When finished, then shutdown kubernetes (minikube) with: `minikube stop`. 
