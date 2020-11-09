from subprocess import Popen, PIPE
import subprocess, os, time
import socket
import sys
import re
from flask import Flask
from flask import request

app = Flask(__name__)


def getCreatedAndStatus(output):
    # Returns tuple of (created,status)
    splitOutput = re.split(r'\s{3,}', str(output))

    return (splitOutput[3], splitOutput[4])

def formatter(node, cassOutput, appOutput, redisOutput, finalOutput):
    # Takes in cassOutput, appOutput, redisOutput and checks if the service is down, appends results to finalOutput array
    
    # Cassandra Status
    if "tcp" not in str(cassOutput):
        finalOutput.append("{:<15}{:<10}\t DOWN\n".format("Cassandra", node))
    else:
        created, status = getCreatedAndStatus(cassOutput)[0], getCreatedAndStatus(cassOutput)[1]
        finalOutput.append("{:<15}{:<10}\t UP \t{:<20}\t{:<20}\n".format("Cassandra", node, created, status))

    # App (URL Shortener) Status
    if "tcp" not in str(appOutput):
        finalOutput.append("{:<15}{:<10}\t DOWN\n".format("URL Shortener", node))
    else:
        created, status = getCreatedAndStatus(appOutput)[0], getCreatedAndStatus(appOutput)[1]
        finalOutput.append("{:<15}{:<10}\t UP \t{:<20}\t{:<20}\n".format("URL Shortener", node, created, status))

    # Redis Status
    if "tcp" not in str(redisOutput):
        finalOutput.append("{:<15}{:<10}\t DOWN\n".format("Redis", node))
    else:
        created, status = getCreatedAndStatus(redisOutput)[0], getCreatedAndStatus(redisOutput)[1]
        finalOutput.append("{:<15}{:<10}\t UP \t{:<20}\t{:<20}\n".format("Redis", node, created, status))

def check_status():
    nodes = []

    with open('nodes') as config_file:
        for line in config_file:
            nodes.append(line.rstrip())

    finalOutput = ["\nURL Shortener System Status\n\n"]
    n = 0
    for node in nodes:

        finalOutput.append("Node {} Status\n".format(n))
        subprocess.run(["exp", "hhhhiotwwg", "ssh", "-o", "StrictHostKeyChecking=no", "student@" + node, "hostname"])
        cassOutput, _ = Popen(["sshpass", "-p", "hhhhiotwwg", "ssh", "-o", "StrictHostKeyChecking=no", "student@" + node, "docker container ls | grep cassandra"], stdout=PIPE, stderr=PIPE).communicate()
        appOutput, _ = Popen(["sshpass", "-p", "hhhhiotwwg", "ssh", "-o", "StrictHostKeyChecking=no", "student@" + node, "docker container ls | grep urlshortner"], stdout=PIPE, stderr=PIPE).communicate()
        redisOutput, _ = Popen(["sshpass", "-p", "hhhhiotwwg", "ssh", "-o", "StrictHostKeyChecking=no", "student@" + node, "docker container ls | grep redis:latest"], stdout=PIPE, stderr=PIPE).communicate()
        # Need to use .stdout
        formatter(node, cassOutput.decode('utf-8'), appOutput.decode('utf-8'), redisOutput.decode('utf-8'), finalOutput)

        n += 1

    return ''.join(finalOutput)


@app.route('/', methods = ['GET'])
def request_handler():
    return '<meta http-equiv="refresh" content="5"><span style="white-space: pre-line">' + check_status() + '</span>'

@app.route('/', methods = ['PUT'])
def request_handler_new_host():
    new_host = request.args.get('host')
    with open('nodes', 'a') as myfile:
        myfile.write(new_host + '\n')
    return 'New node added'

@app.route('/', methods = ['DELETE'])
def request_handler_host_remove():
    old_host = request.args.get('host')
    with open('nodes', 'r') as f:
        lines = f.readlines()
    with open('nodes', 'w') as f:
        for line in lines:
            if line.strip('\n') != old_host:
                f.write(line)
    return 'Node removed'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
