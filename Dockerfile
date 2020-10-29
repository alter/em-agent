FROM python:3-alpine
MAINTAINER Roman Dolgov 'alter.pub@gmail.com'
WORKDIR /app
COPY requirements.txt /app
RUN apk update && \
    apk --no-cache add nmap curl-dev python3-dev libressl-dev gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del python3-dev libressl-dev gcc musl-dev && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ /var/cache/apk/*
COPY . /app
CMD [ "python", "agent.py"]
EXPOSE 8000
