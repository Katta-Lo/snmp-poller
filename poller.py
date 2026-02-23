#!/usr/bin/env python3

import yaml
import json
import subprocess
import time
import sys
import logging
import argparse
import datetime
import pyyaml

# Open file as Python-dictionary

def load_config(path):
	try:
		with open(path, "r") as f:
            		return yaml.safe_load(f)

    	except Exception as e:
		print("Config error:", e)
        	sys.exit(2)

# Validate config

def validate_config(cfg):
    if "targets" not in cfg:
        raise ValueError("Missing targets")

    for t in cfg["targets"]:
        if "ip" not in t:
            raise ValueError("Target is missing ip")
        if "name" not in t:
            raise ValueError("Target is missing name")
        if "community" not in t:
            raise ValueError("Target is missing community")
	if "oids" not in t:
		raise ValueError("Target is missing oid")

#def merge_defaults(defaults, target):

#def build_snmpget_cmd(target, oid):

#def run_snmpget(cmd, timeout_s):

#def poll_target(target):

#main()
