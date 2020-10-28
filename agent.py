#!/usr/bin/env python


from flask import Flask, render_template, make_response
from urllib.parse import urlencode
from yamlreader import yaml_load
from web_check import WebCheck
from pathlib import Path
from queue import Queue
from time import sleep
from io import BytesIO
import threading
import pycurl
import config
import pprint
import yaml
import glob
import os


app = Flask(__name__)
app.secret_key = os.urandom(42)
lock = threading.Lock()
q_web_checks = Queue()
webcheck_results = {}

@app.route('/', methods=['GET','POST'])
def hello():
    return "Hello, it's em-agent. Use /metrics as prometheus endpoint"

@app.route('/metrics', methods=['GET'])
def metrics():
    resp = make_response(render_template("index.html", webcheck_results = webcheck_results))
    resp.headers['Content-type'] = 'text/plain; charset=utf-8'
    return resp

def time_converter(unit):
    unit = str(unit)
    if 's' in unit:
        unit = unit.replace('s', '')
    elif 'm' in unit:
        unit = unit.replace('m', '')
        unit = int(unit) * 60
    elif 'h' in unit:
        unit = unit.replace('h', '')
        unit = int(unit) * 3600
    return float(unit)

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

        sleep(time_converter(webcheck.update_interval))
#        with lock:
#            print(threading.current_thread().name,webcheck.name)

def web_checks_worker():
    while True:
        item = q_web_checks.get()
        make_web_check(item)
        q_web_checks.task_done()

def make_web_checks(check_list):
    num_threads = len(check_list)

    for i in range(num_threads):
        worker = threading.Thread(target=web_checks_worker, daemon=True).start()

    for x in check_list:
        q_web_checks.put(x)

def setup_app(app):
    merge_configs()
    checks_config = load_config()
    make_web_checks(checks_config['web_checks'])
setup_app(app)


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, threaded=True)

