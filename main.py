#!/usr/bin/env python
# @lint-avoid-python-3-compatibility-imports
#
# tcpaccept Trace TCP accept()s.
#           For Linux, uses BCC, eBPF. Embedded C.
#
# USAGE: tcpaccept [-h] [-T] [-t] [-p PID] [-P PORTS] [-4 | -6]
#
# This uses dynamic tracing of the kernel inet_csk_accept() socket function
# (from tcp_prot.accept), and will need to be modified to match kernel changes.
#
# Copyright (c) 2015 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 13-Oct-2015   Brendan Gregg   Created this.
# 14-Feb-2016      "      "     Switch to bpf_perf_output.

import time, _thread, re, socket
from prometheus_client import start_http_server, Summary
from prometheus_client import Gauge, generate_latest
from wotools.tcp_send import tcp_send
from wotools.tcp_receive import tcp_receive
from prometheus_client.core import CollectorRegistry
from flask_basicauth import BasicAuth
from flask import Flask, Response, jsonify, request
import json, re, random, string
from woutils.woredis import WoRedis

app = Flask(__name__)
token = ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))

Redis=WoRedis()

Nowlist=[]
sedNowlist=[]

basic_auth = BasicAuth(app)
hostname = socket.gethostname()

REGISTRY = CollectorRegistry(auto_describe=False)

applink={}

rdata = {}


fields = {
           "edges_fields": [
             {
               "field_name": "id",
               "type": "string"
             },
             {
               "field_name": "source",
               "type": "string"
             },
             {
               "field_name": "target",
               "type": "string"
             },
             {
               "field_name": "mainStat",
               "type": "number"
             },
              {
                "field_name": "secondaryStat",
                "type": "string"
              }
           ],
           "nodes_fields": [
                  {
                    "field_name": "id",
                    "type": "string"
                  },
                  {
                    "field_name": "title",
                    "type": "string"
                  },
                  {
                    "field_name": "subTitle",
                    "type": "string"
                  },
                  {
                    "field_name": "mainStat",
                    "displayName": "All connections ",
                    "type": "string"
                  },
                  {
                    "field_name": "secondaryStat",
                    "displayName": "Closed connections ",
                    "type": "string"
                  },
                  {
                    "color": "green",
                    "field_name": "arc__1",
                    "type": "number",
                    "displayName": "Closed connections"
                  },
                  {
                    "color": "red",
                    "field_name": "arc__2",
                    "type": "number",
                    "displayName": "Unclosed connections"
                  }
                ]
         }

demo_fields = {
                "edges_fields": [
                  {
                    "field_name": "id",
                    "type": "string"
                  },
                  {
                    "field_name": "source",
                    "type": "string"
                  },
                  {
                    "field_name": "target",
                    "type": "string"
                  },
                  {
                    "field_name": "mainStat",
                    "type": "string"
                  },
                  {
                    "field_name": "secondaryStat",
                    "type": "string"
                  }
                ],
                "nodes_fields": [
                  {
                    "field_name": "id",
                    "type": "string"
                  },
                  {
                    "field_name": "title",
                    "type": "string"
                  },
                  {
                    "field_name": "subTitle",
                    "type": "string"
                  },
                  {
                    "field_name": "mainStat",
                    "displayName": "All connections ",
                    "type": "string"
                  },
                  {
                    "field_name": "secondaryStat",
                    "displayName": "Closed connections ",
                    "type": "string"
                  },
                  {
                    "color": "green",
                    "field_name": "arc__1",
                    "type": "number",
                    "displayName": "Closed connections"
                  },
                  {
                    "color": "red",
                    "field_name": "arc__2",
                    "type": "number",
                    "displayName": "Unclosed connections"
                  }
                ]
              }

demo_fields_data =  {
                    	"nodes": [{
                    			"id": "nginx",
                    			"title": "nginx",
                    			"subTitle": "10.244.53.59:6379",
                    			"mainStat": "all:9",
                    			"secondaryStat": "closed:4",
                    			"arc__1": 4,
                    			"arc__2": 4,
                    			"arc__3": 0
                    		},
                    		{
                    			"id": "mysqld",
                    			"title": "mysqld",
                    			"subTitle": "10.244.53.59:2379",
                    			"mainStat": "all: 8",
                    			"secondaryStat": "closed:4",
                    			"arc__1": 0.4444444444444444,
                    			"arc__2": 0.5555555555555556,
                    			"arc__3": 0
                    		},
                    		{
                    			"id": "redis",
                    			"title": "redis",
                    			"subTitle": "10.244.53.59:2379",
                    			"mainStat": "all: 8",
                    			"secondaryStat": "closed:4",
                    			"arc__1": 0.4444444444444444,
                    			"arc__2": 0.5555555555555556,
                    			"arc__3": 0
                    		}
                    	],
                    	"edges": [{
                    		"id": "nginx-redis",
                    		"source": "nginx",
                    		"target": "redis",
                    		"mainStat": "all: 1",
                    		"secondaryStat": "closed: 0"
                    	},
                      {
                    		"id": "nginx-mysql",
                    		"source": "nginx",
                    		"target": "mysql",
                    		"mainStat": "all: 1",
                    		"secondaryStat": "closed: 0"
                    	}
                      ,]
                    }

# @app.route('/metrics',methods=["GET"])
# def metrics():
#     wo_host_send = Gauge('wo_host_send', 'Description of gauge',["pid",'cmd','lsrc','rsrc', 'host'],registry=REGISTRY)
#     wo_host_receive = Gauge('wo_host_receive', 'Description of gauge',["pid",'cmd','lsrc','rsrc', 'host'],registry=REGISTRY)
#     if request.args.get("token") != token:
#       return "no auth",401,{"Content-Type":"application/json"}
#     wo_host_receive.clear()
#     wo_host_send.clear()
#     return Response(generate_latest(REGISTRY),
#     mimetype="text/plain")

@app.route('/api/graph/data',methods=["GET"])
def graph_data():
    #接收的tcp数据  tcp_Nowlist
    #本地发送的数据  tcp_sedNowlist
    if request.args.get("token") != token:
      return "no auth",401,{"Content-Type":"application/json"}
    graphData = {}
    if request.args.get("service"):
        nodes = []
        edges = []
        prefix = request.args.get("service",type=str)
        allService = re.split(",",prefix)
        print("get prefix service %s" %allService)
        for service in allService:
            nodes.append(Redis.getjson("wo-bcc/node-%s" %service))
            sourceEdges = Redis.prefixList("wo-bcc/edges-%s-*" %service)
            targetEdges = Redis.prefixList("wo-bcc/edges-*-%s" %service)
            edges.extend(targetEdges)
            edges.extend(sourceEdges)
            for edgesJson in sourceEdges:
              target = edgesJson["target"]
              nodes.append(Redis.getjson("wo-bcc/node-%s" %target))
            for edgesJson in targetEdges:
              source = edgesJson["source"]
              nodes.append(Redis.getjson("wo-bcc/node-%s" %source))
        nodes = [dict(t) for t in {tuple(d.items()) for d in nodes}]
        graphData["nodes"] = nodes
        graphData["edges"] = edges
        return json.dumps(graphData),{"Content-Type":"application/json"}

    graphData["nodes"] = Redis.prefixList("wo-bcc/node-*")
    graphData["edges"] = Redis.prefixList("wo-bcc/edges-*")
    return json.dumps(graphData),{"Content-Type":"application/json"}

@app.route('/api/graph/fields',methods=["GET"])
def fields_data():
    if request.args.get("token") != token:
      return "no auth",401,{"Content-Type":"application/json"}
    return json.dumps(fields),{"Content-Type":"application/json"}

@app.route('/api/health')
def Health():
    return "ok",200,{"Content-Type":"application/json"}


@app.route('/demo/api/graph/data',methods=["GET"])
def demo_graph_data():
    if request.args.get("token") != token:
      return "no auth",401,{"Content-Type":"application/json"}
    return json.dumps(demo_fields_data),{"Content-Type":"application/json"}

@app.route('/demo/api/graph/fields',methods=["GET"])
def demo_data():
    if request.args.get("token") != token:
      return "no auth",401,{"Content-Type":"application/json"}
    return json.dumps(demo_fields),{"Content-Type":"application/json"}

@app.route('/demo/api/health',methods=["GET"])
def demo_Health():
    return "ok",200,{"Content-Type":"application/json"}


if __name__ == "__main__":
    tcp_send()
    tcp_receive()
    print("token:",token)
    #app.run(host='0.0.0.0',port=9100,debug=True)
    app.run(host='0.0.0.0',port=9100)
