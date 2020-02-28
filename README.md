# buttonflux
Python3.x Command Line Utility for saving Button Presses from standard interfaces into InfluxDB via UDP

## Installation and Development

### Installation
Read `evdev` [documentation](https://python-evdev.readthedocs.io/en/latest/install.html)

Clone the repository to your machine and use `pip` to install the CLI:

    pip install .

### Development
develop using `venv` as follows:

    python -m venv venv

activate the virtual environment, install using:

    python install -e .

## Usage
```
usage: buttonflux.py [-h] --config CONFIG

CLI for Logging Button Press Events to InfluxDB and publishing via MQTT

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  configuration conf.json file with path.
```

### Example

Typical Example:

1. Setup InfluxDB's configuration (`influxdb.conf`) by adding a UDP port to read Button information:

        [[udp]]
          enabled = true
          bind-address = ":8086"
          database = button
          precision = "ms"

2. Run the script using:

        buttonflux --config /path/to/conf.json

Data will be stored in `button` Database.
