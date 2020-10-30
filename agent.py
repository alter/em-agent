#!/usr/bin/env python


from flask import Flask, render_template, make_response
from time_converter import TimeConverter
from yamlreader import yaml_load
from port_check import PortCheck
from web_check import WebCheck
from queue import Queue
from time import sleep
import threading
import config
import yaml
import os


app = Flask(__name__)
app.secret_key = os.urandom(42)
lock = threading.Lock()
q_web_checks = Queue()
q_port_checks = Queue()
webcheck_results = {}
portcheck_results = {}


@app.route('/', methods=['GET', 'POST'])
def hello():
    return "Hello, it's em-agent. Use /metrics as prometheus endpoint"


@app.route('/metrics', methods=['GET'])
def metrics():
    resp = make_response(render_template("index.html",
                         webcheck_results=webcheck_results,
                         portcheck_results=portcheck_results))
    resp.headers['Content-type'] = 'text/plain; charset=utf-8'
    return resp


def merge_configs():
    yamlconfig = yaml_load(config.CHECKS_FOLDER)
    with open(config.DEFAULT_CONFIG, 'wt') as out:
        print(yaml.dump(yamlconfig, default_flow_style=False), file=out)


def load_config():
    with open(config.DEFAULT_CONFIG, 'r') as fp:
        yamlconfig = yaml.safe_load(fp)
    return yamlconfig


def make_web_check(item):
    while True:
        webcheck = WebCheck(item)
        webcheck.make_request()
        webcheck_results[webcheck.name] = webcheck.success
        sleep(int(TimeConverter(webcheck.update_interval)))


def web_checks_worker():
    while True:
        item = q_web_checks.get()
        make_web_check(item)
        q_web_checks.task_done()


def make_web_checks(check_list):
    num_threads = len(check_list)
    for i in range(num_threads):
        threading.Thread(target=web_checks_worker, daemon=True).start()
    for x in check_list:
        q_web_checks.put(x)


def make_port_check(item):
    while True:
        portcheck = PortCheck(item)
        portcheck.make_request()
        portcheck_results[portcheck.name] = portcheck.success
        sleep(int(TimeConverter(portcheck.update_interval)))


def port_checks_worker():
    while True:
        item = q_port_checks.get()
        make_port_check(item)
        q_port_checks.task_done()


def make_port_checks(check_list):
    num_threads = len(check_list)
    for i in range(num_threads):
        threading.Thread(target=port_checks_worker, daemon=True).start()
    for x in check_list:
        q_port_checks.put(x)


def setup_app(app):
    merge_configs()
    checks_config = load_config()
    make_web_checks(checks_config['web_checks'])
    make_port_checks(checks_config['port_checks'])


setup_app(app)


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, threaded=True)
