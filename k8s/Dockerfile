FROM python:3.9

WORKDIR /app 

RUN apt-get update && apt-get upgrade -y 
COPY ./src .

CMD ["python3", "mimic_process.py"]
