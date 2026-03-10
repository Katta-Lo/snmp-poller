#!/usr/bin/env python3

import yaml
import json
import subprocess
import time
import sys
import logging
import argparse
import datetime


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

#Combine defaults with target values, overriding defaults when provided

def merge_defaults(defaults, target):
    result = defaults.copy() #copy of defaults, not changing the original
    for key in target:
        result[key] = target[key]
    return result

# Builds the snmpget-command

def build_snmpget_cmd(target, oid):
    return [
        "snmpget",
        "-v", "2c",
        "-c",
        target["community"],
        target["ip"],
        oid
    ]

# Execute an SNMP GET command using subprocess, capture output or errors, and measure execution time

def run_snmpget(cmd, timeout_s):
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s
        )

        elapsed = time.time() -start

        if result.returncode == 0:
            return True, result.stdout.strip(), elapsed
        else:
            return False, result.stderr.strip(), elapsed

    except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            return False, "timeout", elapsed

#SNMP-polling
def poll_target(target):
    logging.info("Starting target %s (%s)", target["name"], target["ip"])

    start_time = time.time()
    budget = target.get("target_budget_s", 10)
    timeout = target.get("timeout_s", 2.5)
    retries = target.get("retries", 1)

    results = {}
    ok_count = 0
    fail_count = 0

    oids = target.get("oids", [])

    for oid in oids:
        #Check time budget
        if time.time() - start_time > budget:
            logging.warning("Time budget exceeded for %s", target["name"])
            break

        attempt = 0
        success = False

        while attempt <= retries and not success:
            cmd = build_snmpget_cmd(target, oid)
            ok, value, elapsed = run_snmpget(cmd, timeout)

            if ok:
                results[oid] = {
                    "ok": True,
                    "value": value,
                    "elapsed": elapsed
                }
                ok_count = ok_count + 1
                success = True
            else:
                if value == "timeout":
                    logging.warning("Timeout on %s (%s), retry %d", target["name"], oid, attempt)
                    attempt = attempt + 1
                else:
                    #Auth or other error = fail fast
                    results[oid] = {
                        "ok": False,
                        "error": value
                    }
                    fail_count = fail_count + 1
                    break

        if not success and oid not in results:
            results[oid] = {
                "ok": False,
                "error": "timeout"
            }
            fail_count = fail_count + 1

    runtime = time.time() - start_time

    if ok_count > 0 and fail_count == 0:
        status = "ok"
    elif ok_count > 0:
        status = "partial"
    else:
        status = "failed"

    if status == "ok":
        logging.info("Finished target %s status=%s runtime=%.2f",
                 target["name"], status, runtime)
    elif status == "partial":
        logging.warning("Finished target %s status=%s runtime=%.2f",
                    target["name"], status, runtime)
    else:  # failed
        logging.error("Finished target %s status=%s runtime=%.2f",
                  target["name"], status, runtime)


    return {
        "name": target["name"],
        "ip": target["ip"],
        "ok_count": ok_count,
        "status": status,
        "fail_count": fail_count,
        "runtime": runtime,
        "results": results
    }

def main():
#Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)     #Config YAML-file
    parser.add_argument("--out", required=True)        #Output JSON
    parser.add_argument("--log-level", default="INFO") #Logging level

    args = parser.parse_args()

#Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(levelname)s %(message)s"
    )

#Record start time
    run_start = time.time()

#Load and validate config
    cfg = load_config(args.config)   #Load YAML into Python

#Check that config has required keys

    try:
        validate_config(cfg)
    except Exception as e:
        logging.error("Invalid config %s", e)
        sys.exit(2)

#Prepare defaults and results
    defaults = cfg.get("defaults", {})
    all_results = []

    logging.info("Starting run with %d targets", len(cfg["targets"]))

#Poll each target
    for t in cfg["targets"]:
        merged = merge_defaults(defaults, t)
        result = poll_target(merged)
        all_results.append(result)

#Generate output dict.
    duration = time.time() - run_start

    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config_file": args.config,
        "duration": duration,
        "targets": all_results
    }

#Save results to JSON
    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)

#Exit codes based on results
    total_ok = sum(t.get("ok_count", 0) for t in all_results)
    total_fail = sum(t.get("fail_count", 0) for t in all_results)

    if total_ok > 0 and total_fail == 0:
        return 0
    elif total_ok > 0:
        return 1
    else:
        return 2

if __name__ == "__main__":
        sys.exit(main())
