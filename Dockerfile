FROM python:slim
ADD . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
