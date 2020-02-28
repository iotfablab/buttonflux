#!/usr/bin/env python3
# Python3.x Command Line Utility for
# saving Button Presses from standard Linux Interfaces (/dev/input/eventX)
# into InfluxDB via UDP and publishing them via MQTT
# Changes:
#       - Change `measurement` dict
#       - Add Line Protocol String
#       - Add MQTT Publishing
#       - Linting

import os
import sys
import json
import logging
import argparse
import concurrent.futures
import evdev
from influxdb import InfluxDBClient, line_protocol
from influxdb.client import InfluxDBClientError
import paho.mqtt.publish as publish

# Logger Settings
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

handler = logging.FileHandler("/var/log/buttonflux.log")
handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s-%(name)s-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

DEVICE = ''
hw_dev = None
db_client = None
button_conf = dict()
mqtt_conf = dict()


def publish_data(lineprotocol_data):
    """ Publish Line Protocol String to dedicated MQTT Topic"""
    lp_array = lineprotocol_data.split('\n')
    lp_array.pop()
    global button_conf
    global mqtt_conf
    global DEVICE

    for topic in button_conf['topics']:
        pload = lp_array[button_conf['topics'].index(topic)]
        try:
            publish.single(
                DEVICE + '/' + topic,
                payload=pload,
                qos=1,
                hostname=mqtt_conf['broker'],
                port=mqtt_conf['port'])
            return True
        except Exception as e:
            logger.error('MQTT Publish Exception: {}'.format(e))
            return False


def save_to_db(measurements):
    """ Save button press event to InfluxDB"""
    global db_client
    try:
        db_client.send_packet(measurements)
        return True
    except InfluxDBClientError as influx_e:
        logger.error({'Error while UDP Sending: {e}'.format(e=influx_e)})
        return False


def read_event(device):
    """ Read Button Press Event for given Hardware Device Port"""
    global hw_dev
    hw_dev = evdev.InputDevice(device)
    logger.debug('EVDEV Input Device Created: {}'.format(hw_dev))
    logger.info('Reading from Device: {}'.format(hw_dev))
    try:
        for event in hw_dev.read_loop():
            if event.value == 1:
                logger.info('Button Pressed')
                logger.debug(event)
                event_measurement = {
                    "tags": {
                        "source": "button"
                    },
                    "points": [
                        {
                            "measurement": "eventlog",
                            "time": int(event.timestamp() * (1e9)),
                            "fields": {
                                "pressed": event.value,
                            }
                        }
                    ]
                }
                logger.debug(line_protocol.make_lines(event_measurement))
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    if executor.submit(publish_data, line_protocol.make_lines(event_measurement)).result():
                        logger.info('Published Event to MQTT')
                    if executor.submit(save_to_db, event_measurement).result():
                        logger.info('Data saved to InfluxDB')
    except Exception as e:
        logger.error('Exception while Reading Event: {}'.format(e))
        hw_dev.close()
        db_client.close()
        sys.exit(2)


def file_path(path_to_file):
    """ Check if Path and File exist for configuration"""
    if os.path.exists(path_to_file):
        if os.path.isfile(path_to_file):
            logger.info('File Exists')
            with open(path_to_file) as conf_file:
                return json.load(conf_file)
        else:
            logger.error('Configuration File Not Found')
            raise FileNotFoundError(path_to_file)
    else:
        logger.error('Path to Configuration File Not Found')
        raise NotADirectoryError(path_to_file)


def parse_args():
    """ Pass Arguments for Configuration File"""
    parser = argparse.ArgumentParser(description='CLI for Logging Button Press Events to InfluxDB and publishing via MQTT')
    parser.add_argument('--config', type=str, required=True, help='configuration conf.json file with path.')
    return parser.parse_args()


def main():
    args = parse_args()

    CONF = file_path(args.config)

    global DEVICE
    DEVICE = CONF['deviceID']

    global button_conf
    button_conf = CONF['button']
    influx_conf = CONF['influx']

    global mqtt_conf
    mqtt_conf = CONF['mqtt']

    logger.info('Creating InfluxDB Client')
    logger.debug('Client for {influx_host}@{influx_port} with udp:{udp_port}'.format(
        influx_host=influx_conf['host'],
        influx_port=influx_conf['port'],
        udp_port=button_conf['udp_port']))

    global db_client
    db_client = InfluxDBClient(
        host=influx_conf['host'],
        port=influx_conf['port'],
        use_udp=True,
        udp_port=button_conf['udp_port'])

    logger.info('Checking Connectivity to InfluxDB')
    try:
        if db_client.ping():
            logger.info('Connected to InfluxDB')
        else:
            logger.error('Cannot Connect to InfluxDB. Check Configuration/Connectivity')
    except Exception as connection_e:
        logger.error(connection_e)
        db_client.close()
        sys.exit(1)

    logger.info('Setting up Reading Button Events')
    try:
        read_event(button_conf['hw_device'])
    except KeyboardInterrupt:
        print('CTRL+C hit for Script')
        hw_dev.close()
        db_client.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
