This application performs automated SNMP polling against one or more network devices.
Targets, credentials, and OIDs are defined in a YAML configuration file.
The script polls each device, handles timeouts and retries, and outputs all results as JSON-file.
Logging is available with INFO, WARNING, and ERROR levels.


Files and their functions:

poller.py	Main application. Loads config, polls devices, handles timeouts, logging, and JSON output.

config.yml	Configuration file containing targets, defaults, and OIDs.

test_config.py	Simple unit test verifying that the configuration is read and validated correctly.

README.md	Documentation for installation and usage.


Methods:

load_config(path)
Input: File path
Output: Python dictionary
Description: Loads a YAML configuration file and returns it as a dictionary.

validate_config(cfg)
Input: Configuration dictionary
Output: None (raises ValueError on error)
Description: Ensures required fields exist for each target.

merge_defaults(defaults, target)
Input: Two dictionaries
Output: Merged dictionary
Description: Combines default values with target specific values.

build_snmpget_cmd(target, oid)
Input: Target dictionary, OID
Output: List representing a subprocess command
Description: Builds the SNMP GET command for snmpget.

run_snmpget(cmd, timeout_s)
Input: Command list, timeout
Output: Tuple (success, output, elapsed_time)
Description: Executes the SNMP command with timeout handling.

poll_target(target)
Input: Target dictionary
Output: Result dictionary
Description: Polls all OIDs for a target, handles retries, time budgets, and logging.

main()
Input: Command line arguments
Output: Exit code
Description: Orchestrates the full application: config loading, polling, JSON output, and exit codes.

Dependencies between methods:
main() calls load_config(), which in turn calls validate_config().

main() also calls poll_target(), which internally uses build_snmpget_cmd() and then run_snmpget().


Installation:

Requirements
Python 3
Operating system: Linux (SNMP tools required)


Install PyYAML:
pip install pyyaml

Install SNMP tools (example for Debian/Ubuntu):
sudo apt install snmp

How to Run:

Basic usage:

python poller.py --config config.yml --out out.json


With custom log level:

python poller.py --config config.yml --out out.json --log-level INFO

Argument Description:

--config	Path to YAML configuration file
--out	        Output JSON file (use - for stdout)
--log-level	Logging level: INFO, WARNING, ERROR

Examples:

Run with INFO logging:
python poller.py --config config.yml --out output.json --log-level INFO

Run with only warnings and errors:
python poller.py --config config.yml --out - --log-level WARNING

Example Log Output:

INFO Starting run with 2 targets
INFO Starting target Switch (172.16.0.250)
INFO Finished target Switch status=ok runtime=0.21
INFO Starting target Localhost (127.0.0.1)
INFO Finished target Localhost status=ok runtime=0.08

Example JSON Output:

{
  "timestamp": "2026-03-03T14:31:46",
  "config_file": "config.yml",
  "duration": 0.3036010265350342,
  "targets": [
    {
      "name": "Switch",
      "ip": "172.16.0.250",
      "ok_count": 3,
      "status": "ok",
      "fail_count": 0,
      "runtime": 0.2110137939453125,
      "results": {
        "ifOperStatus.1": {
          "ok": true,
          "value": "IF-MIB::ifOperStatus.1 = INTEGER: down(2)",
          "elapsed": 0.12360787391662598
        },

Exit Codes:

0 – All targets OK

1 – Partial success

2 – Total failure or invalid config

Unit Test:

The project includes one unit test for configuration validation.
The test verifies that a configuration missing the required targets key raises a ValueError.

Run unittest with: python -m unittest -v
