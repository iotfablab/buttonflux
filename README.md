# buttonflux
Python3.x Command Line Utility for saving Button Presses from standard interfaces into InfluxDB via UDP

## Installation and Development

### Installation
 Clone the repository to your machine and use `pip` to install the CLI:

    pip install .

### Development
develop using `venv` as follows:

    python -m venv venv

activate the virtual environment, install using:

    python install -e .

## Usage

You can create a Configuration JSON file and adapt the `CONF_PATH` in the `buttonflux\buttonflux.py` file and execute:

    buttonflux

This will read the minimum configuration like the `device` and `udp_port` from the JSON file

```
usage: buttonflux.py [-h] [--device DEVICE] [--udp-port UDP_PORT]
                     [--db-host DB_HOST] [--db-port DB_PORT]

CLI for Logging Button Press Events to InfluxDB

optional arguments:
  -h, --help           show this help message and exit
  --device DEVICE      Device for Button Event. E.g. /dev/input/event0
  --udp-port UDP_PORT  UDP Port for sending information via UDP. Should be
                       configured in InfluxDB
  --db-host DB_HOST    hostname for InfluxDB HTTP Instance. Default: localhost
  --db-port DB_PORT    port number for InfluxDB Instance. Default: 8086
```

### Example

Typical Example:

1. Setup InfluxDB's configuration (`influxdb.conf`) by adding a UDP port to read Button information:

        [[udp]]
          enabled=true
          bind-address=":8100"
          database=button
          precision='ms'

2. Run the script using:

        buttonflux --device /dev/input/event1 --udp-port 8100

Data will be stored in `button` Database.
