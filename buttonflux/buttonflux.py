import sys
import json
import logging
import argparse

import evdev
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

handler = logging.FileHandler("/var/log/buttonflux.log")
handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s-%(name)s-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


dev = None
db_client = None
CONF_PATH = '/etc/umg/conf.json'

def parse_args():
    parser = argparse.ArgumentParser(description='CLI for Logging Button Press Events to InfluxDB')
    parser.add_argument('--device', type=str, required=False, default='/dev/input/event0',
                            help='Device for Button Event. E.g. /dev/input/event0')
    parser.add_argument('--udp-port', type=int, required=False, default=8096,
                        help='UDP Port for sending information via UDP.\n Should be configured in InfluxDB')
    parser.add_argument('--db-host', type=str, required=False, default='localhost',
                        help='hostname for InfluxDB HTTP Instance. Default: localhost')
    parser.add_argument('--db-port', type=int, required=False, default=8086,
                        help='port number for InfluxDB Instance. Default: 8086')
    return parser.parse_args()

def send_data(device, db_host, db_port, udp_port):
    global dev
    dev = evdev.InputDevice(device)
    print(dev)
    logger.debug('Device: {}'.format(dev))

    global db_client
    try:
        db_client = InfluxDBClient(host=db_host, port=db_port, use_udp=True, udp_port=udp_port)
    except InfluxDBClientError as e:
        logger.exception(e)
        raise(e)
    logger.info('Reading from Device: {}'.format(dev))

    for event in dev.read_loop():
        if event.value  == 1:
            logger.info(event)
            logger.info('Button Pressed')
            event_measurement = {
                    'time': int(event.timestamp() * (10 ** 6)),
                    'points': [
                        {
                            'measurement': 'button',
                            'fields': {
                                'pressed': event.value
                            }
                        }
                    ] 
                }
            try:
                db_client.send_packet(event_measurement, time_precision='ms')
                logger.info('event logged')
            except Exception as e:
                logger.exception(e)
    
    


def main():
    args = parse_args()

    CONF = dict()

    if len(sys.argv) == 1:
        logger.info('starting script in default mode')
        logger.debug('CONF FILE: %s' % CONF_PATH)
        with open(CONF_PATH) as cFile:
            _conf = json.load(cFile)
            CONF = _conf['button']
            logger.debug('CONF: ' + json.dumps(CONF))
        
        try:
            send_data(device=CONF['device'],
                    db_host=args.db_host,
                    db_port=args.db_port,
                    udp_port=CONF['dbConf']['udp_port'])
        except KeyboardInterrupt:
            logger.exception('CTRL+C Hit.')
            dev.close()
            db_client.close()
            sys.exit(0)
    

    if len(sys.argv) > 1:
        if args.device is None:
            print('Using default: /dev/input/event0')
        if args.udp_port is None:
            print('Provide UDP Port for InfluxDB')
            sys.exit(1)
        else:
            try:
                send_data(device=args.device,
                    db_host=args.db_host,
                    db_port=args.db_port,
                    udp_port=args.udp_port)
            except KeyboardInterrupt:
                logger.exception('CTRL+C Hit')
                dev.close()
                db_client.close()
                sys.exit(0)

if __name__ == "__main__":
    main()
