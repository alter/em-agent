#!/usr/bin/env python

from flask import Flask, render_template, make_response
from multiprocessing import Process, Queue, cpu_count, Manager
import threading
import logging
import time
import yaml
import config
import os
from port_check import PortCheck
from web_check import WebCheck
from yamlreader import yaml_load  # Importing yaml_load from yamlreader module


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

app = Flask(__name__)
app.secret_key = os.urandom(42)

# Creating multiprocessing queues
q_checks = Queue()

# Results dictionaries
manager = Manager()
webcheck_results = manager.dict()
portcheck_results = manager.dict()


@app.route('/', methods=['GET', 'POST'])
def hello():
    return "Hello, it's em-agent. Use /metrics as prometheus endpoint"


@app.route('/metrics', methods=['GET'])
def metrics():
    logging.info(f"Webcheck Results: {webcheck_results}")
    logging.info(f"Portcheck Results: {portcheck_results}")
    resp = make_response(render_template("index.html",
                         webcheck_results=webcheck_results,
                         portcheck_results=portcheck_results))
    resp.headers['Content-type'] = 'text/plain; charset=utf-8'
    return resp

def merge_configs():
    yamlconfig = yaml_load(config.CHECKS_FOLDER)
    with open(config.DEFAULT_CONFIG, 'wt') as out:
        print(yaml.dump(yamlconfig, default_flow_style=False), file=out)
    logging.info("Merging configurations...")


def load_config():
    merge_configs()
    logging.info("Loading configuration...")
    with open(config.DEFAULT_CONFIG, 'r') as fp:
        yamlconfig = yaml.safe_load(fp)
    logging.info(f"Loaded configuration size: {len(yamlconfig)}")
    return yamlconfig


def check_worker(queue):
    while True:
        while not queue.empty():
            item = queue.get()
            try:
                # Perform the check (WebCheck or PortCheck)
                if 'url' in item:
                    webcheck = WebCheck(item)
                    webcheck.make_request()
                    webcheck_results[item['name']] = webcheck.success
                else:
                    portcheck = PortCheck(item)
                    portcheck.make_request()
                    portcheck_results[item['name']] = portcheck.success
            except Exception as e:
                logging.error(f"Error processing check {item['name']}: {e}")
        # Wait for 1 hour before next round of checks
        logging.info("All checks processed. Waiting for 1 hour before next round.")
        time.sleep(3600)


def distribute_checks(checks):
    logging.info(f"Distributing {len(checks)} checks...")
    for check in checks:
        q_checks.put(check)
    logging.info("Checks distributed to the queue.")


def refresher():
    while True:
        time.sleep(3600)  # 1 hour
        logging.info("Reloading configuration and refilling queue...")
        checks_config = load_config()
        distribute_checks(checks_config['web_checks'] + checks_config['port_checks'])
        logging.info("Configuration reloaded and queue refilled. Next reload in 1 hour.")


def setup_app(app):
    # Load and distribute the initial checks before starting worker processes
    checks_config = load_config()
    distribute_checks(checks_config['web_checks'] + checks_config['port_checks'])

    # Create and start worker processes
    num_processes = cpu_count() * 8
    for _ in range(num_processes):
        p = Process(target=check_worker, args=(q_checks,))
        p.daemon = True
        p.start()

    # Start the configuration refresher in a separate thread
    refresher_thread = threading.Thread(target=refresher)
    refresher_thread.daemon = True
    refresher_thread.start()

if __name__ == "__main__":
    setup_app(app)
    app.run(host=config.HOST, port=config.PORT)
