# Use a specific version of the python:3-alpine image for reproducibility
FROM python:3.12-alpine

# It's good practice to avoid using personal email addresses directly in Dockerfiles
LABEL maintainer="alter.pub@gmail.com"

WORKDIR /app

# Copy only the requirements.txt initially to leverage Docker cache
COPY requirements.txt /app/

# Update apk and install dependencies in one RUN command to reduce image layers
RUN apk update && \
    apk upgrade && \
    apk add --no-cache nmap curl-dev python3-dev openssl-dev gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt

# After pip install, remove unnecessary packages to reduce image size
RUN apk del python3-dev libressl-dev gcc musl-dev && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ /var/cache/apk/*

# Copy the rest of your application
COPY . /app

# Expose port 8000 for your application
EXPOSE 8000

# Set the default command for the container
CMD ["python", "agent.py"]
