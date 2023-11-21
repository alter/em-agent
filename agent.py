#!/usr/bin/env python

import os
import yaml
import logging
import multiprocessing
from datetime import datetime, timedelta
import time
from flask import Flask, render_template, make_response
import config
from port_check import PortCheck
from web_check import WebCheck

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
app.secret_key = os.urandom(42)
manager = multiprocessing.Manager()
webcheck_results = manager.dict()
portcheck_results = manager.dict()


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
    checks_folder = config.CHECKS_FOLDER
    yamlconfig = {}
    for filename in os.listdir(checks_folder):
        if filename.endswith('.yaml'):
            file_path = os.path.join(checks_folder, filename)
            with open(file_path, 'r') as file:
                file_config = yaml.safe_load(file)
                yamlconfig.update(file_config)  # Merging the configuration

    with open(config.DEFAULT_CONFIG, 'wt') as out:
        yaml.dump(yamlconfig, out, default_flow_style=False)


def load_config():
    with open(config.DEFAULT_CONFIG, 'r') as fp:
        return yaml.safe_load(fp)


def TimeConverter(interval):
    if interval.endswith('s'):
        return int(interval[:-1])
    elif interval.endswith('m'):
        return int(interval[:-1]) * 60
    elif interval.endswith('h'):
        return int(interval[:-1]) * 60 * 60
    elif interval.endswith('d'):
        return int(interval[:-1]) * 60 * 60 * 24
    elif interval.endswith('w'):
        return int(interval[:-1]) * 60 * 60 * 24 * 7
    else:
        return int(interval)  # Assuming default is seconds


def worker(task_queue, result_dict):
    while True:
        item = task_queue.get()
        if item is None:
            break  # Exit condition

        if 'url' in item:  # Assuming presence of 'url' indicates a WebCheck
            web_check = WebCheck(item)
            result = web_check.make_request()  # Perform the check
            result_dict[item['name']] = result
        elif 'port' in item:  # Assuming presence of 'port' indicates a PortCheck
            port_check = PortCheck(item)
            result = port_check.make_request()  # Perform the check
            result_dict[item['name']] = result
        else:
            logging.error(f"Unknown check type for item: {item}")
            continue


def start_checks(check_list, result_dict, task_queue):
    num_cpus = multiprocessing.cpu_count()
    num_workers = min(2 * num_cpus, len(check_list))

    for _ in range(num_workers):
        multiprocessing.Process(target=worker, args=(task_queue, result_dict)).start()


def scheduler(task_queue, checks_config):
    next_run_times = {}

    while True:
        current_time = datetime.now()
        for check_type in ['web_checks', 'port_checks']:
            for item in checks_config[check_type]:
                interval = item.get('update_interval', '60')  # Use default if not provided
                next_run_time = next_run_times.get(item['name'], current_time)

                if current_time >= next_run_time:
                    task_queue.put(item)
                    next_run_times[item['name']] = current_time + timedelta(seconds=TimeConverter(interval))

        time.sleep(1)  # Sleep to prevent constant CPU usage


def setup_app(app):
    merge_configs()
    checks_config = load_config()
    print(checks_config)

    task_queue = multiprocessing.Queue()

    # Start worker processes
    start_checks(checks_config['web_checks'], webcheck_results, task_queue)
    start_checks(checks_config['port_checks'], portcheck_results, task_queue)

    # Start scheduler process
    scheduler_process = multiprocessing.Process(target=scheduler, args=(task_queue, checks_config))
    scheduler_process.start()


if __name__ == "__main__":
    setup_app(app)
    app.run(host=config.HOST, port=config.PORT, threaded=True)
