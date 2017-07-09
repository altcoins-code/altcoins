FROM python:slim
ADD . /app
ADD .ssh /root/.ssh
RUN chmod 600 /root/.ssh/id_rsa /root/.ssh/config

WORKDIR /app
RUN apt-get update && apt-get -y install git-core
RUN pip install --no-cache-dir -r requirements.txt
