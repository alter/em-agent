# External Monitoring Agent (EM-Agent)
EM-Agent is an efficient, easy-to-use, and highly customizable monitoring tool designed to help you keep an eye on your web services and ports. It is compatible with Prometheus, which allows you to easily collect, visualize, and alert on the metrics that EM-Agent gathers.

## Key Features
- **Web service monitoring**: EM-Agent can perform GET and POST checks on your web services, giving you immediate feedback on their status.
- **Port monitoring**: EM-Agent can check the state of both TCP and UDP ports, ensuring that your services are accessible.
- **Customizable checks**: Define your own rules for checks using a simple YAML configuration. Modify request methods, timeouts, update intervals, and expected HTTP return codes to suit your needs.
- **Prometheus compatibility**: Metrics are exposed at a /metrics endpoint in a format that ✅Prometheus can scrape, allowing you to leverage Prometheus's powerful data collection and alerting capabilities.

## Conception(one of use-cases, you can use it just as an external web-/port- checker.
![conception](conception.jpg)  
1. Developers/QA/Devops/etc describe rules with items for monitoring and push them to git
2. Monitoring agents(em-agent) make a `git pull` periodically(for example by cron), if there are any changes - restart em-agent
3. em-agent outcome could be found at /metrics endpoint
4. Prometheus(or Zabbix5) has to take data from em-agents
5. Create graphics in grafana
6. Write triggers and push alerts to messangers(discord/telegram/slack/etc)
7. Developers/QA/Devops/etc can get results as graphics and alerts

[github](https://github.com/alter/em-agent)  

## Rules examples
Look up for examples in a *checks* folder  

# Installation
## Requirements
Before you begin, ensure you have met the following requirements:

- You have a machine with Python 3.5 or later installed.  
- You have the following Python packages installed: Flask, PyYAML, PyCurl, and python-nmap.  
- You have installed the necessary system dependencies: libssl-dev, libcurl4-openssl-dev, and python3-dev.  

## Docker container
`docker run -d --rm -v /opt/em-agent-checks:/app/checks -p 8000:8000 alter/em-agent`  

## Configure
Check config.py, you can put any yaml files in config.CHECKS_FOLDER  

# Usage
## Put checks in yaml format
You can set not all options, in that case default values will be used  
## WebChecks
It's possible to make GET and POST checks at this moment  
```yaml
web_checks:
  - name: zabbix
    url: zabbix.wvservices.com
    scheme: https
    method: get
    timeout: 5s
    update_interval: 15s
    return_http_code: 304
  - name: waves.exchange
    url: waves.exchange
    scheme: https
    method: get
    timeout: 10s
    update_interval: 30s
  - name: postman post
    url: postman-echo.com/post
    scheme: https
    method: post
    timeout: 15s
    postfields: text=super&pass=oops&user=lamer
```

### Default values
```yaml
name: unreal-ip
url: 256.256.256.256
scheme: https
method: get
request_timeout: 3
connection_timeout: 3
update_interval: 60
return_http_code: 200
arguments:
postfields:
application_json: False
follow_redirect: False
```

### Results
*0* - fail
*1* - success

## PortChecks
It's possible to check TCP and UDP ports

```yaml
port_checks:
  - name: mainnet-aws-fr-2.wavesnodes.com data tcp
    host: mainnet-aws-fr-2.wavesnodes.com
    port: 6868
    protocol: tcp
    update_interval: 1m
  - name: mainnet-aws-fr-1.wavesnodes.com api udp
    host: mainnet-aws-fr-1.wavesnodes.com
    port: 6869
    protocol: udp
    connection_timeout: 10s
    update_interval: 5m
  - name: localhost tcp
    host: 127.0.0.1
    port: 8000
    protocol: tcp
    connection_timeout: 1s
    update_interval: 30s
```

### Default values
```yaml
name: unreal-ip
host: 256.256.256.256
port: 65536
protocol: tcp
connection_timeout: 10
update_interval: 60
```

### Results
*0* - fail(port in 'close' state or host isn't accessible)
*1* - success(port in 'open' state)
*2* - IDK(port in 'open|filtered' state)


### How to run application
Launch `./agent.py`  
Check [http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics)  

example:  
```yaml
web_em_check{label="localhost"} 1
web_em_check{label="waves.exchange"} 1
web_em_check{label="zabbix"} 0
web_em_check{label="postman post"} 1
web_em_check{label="web3tech.ru"} 1

port_em_check{label="mainnet-aws-fr-2.wavesnodes.com data tcp"} 0
port_em_check{label="mainnet-aws-fr-1.wavesnodes.com data tcp"} 1
port_em_check{label="localhost tcp"} 1
port_em_check{label="mainnet-aws-fr-1.wavesnodes.com api tcp"} 1
port_em_check{label="mainnet-aws-fr-1.wavesnodes.com api udp"} 2
```

## Apply changes
Restart application for using new checks  
