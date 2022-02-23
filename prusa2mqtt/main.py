#!/usr/bin/env python
import re
from json import dumps
import serial
import sys
import time

import paho.mqtt.client as mqtt

PRUSA_BAUDRATE = 115200
# 'T:26.1 /0.0 B:25.6 /0.0 T0:26.1 /0.0 @:0 B@:0 P:27.3 A:33.8' <- example line
PATTERN_START = re.compile(r'.*start\n')
PATTERN_END = re.compile(r'.*INT4\n')

PATTERN_TEMP_ACTIVE = re.compile(r'T:(?P<extruder_actual>\d+\.\d+) /(?P<extruder_target>\d+\.\d+) B:(?P<bed_actual>\d+\.\d+) /(?P<bed_target>\d+\.\d+) T0:(\d+\.\d+) /(\d+\.\d+) @:(?P<hotend_power>\d+) B@:(?P<bed_power>\d+) P:(?P<pinda>\d+\.\d+) A:(?P<ambient>\d+\.\d+)')

# 'T:206.65 E:0 B:59.4' <- example line
PATTERN_TEMP_IDLE = re.compile(r'T:(?P<extruder_actual>\d+\.\d+) E:(?P<e>\d+) B:(?P<bed_actual>\d+\.\d+)')

# 'NORMAL MODE: Percent done: 93; print time remaining in mins: 2; Change in mins: -1' <- example line
PATTERN_PROGRESS = re.compile(r'\w+ MODE: Percent done: (?P<percent_done>\d+); print time remaining in mins: (?P<mins_remaining>\d+); Change in mins: (?P<change_in_mins>-?\d+)')

PATTERN_TOPICS = {
    PATTERN_TEMP_ACTIVE: 'temp',
    PATTERN_TEMP_IDLE: 'temp_idle',
    PATTERN_PROGRESS: 'progress',
}


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Log temperature data from the USB port of a Prusa printer to an MQTT server.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--serial_port', help='Path to the serial port device.', default='/dev/ttyACM0')
    parser.add_argument('--topic', help='Topic for the MQTT message.', default='prusa')
    parser.add_argument('--client_id', help='Distinct client ID for the MQTT connection.', default='prusa2mqtt')
    parser.add_argument('--check_interval', help='Interval in seconds for checking the temperatures.', type=int, default=5)
    parser.add_argument('--mqtt_address', help='Address for the MQTT connection.', default='localhost')
    parser.add_argument('--mqtt_port', help='Port for the MQTT connection.', type=int, default=1883)
    parser.add_argument('--mqtt_username', help='User name for the MQTT connection.', default=None)
    parser.add_argument('--mqtt_password', help='Password name for the MQTT connection.', default=None)
    parser.add_argument('--discrete_topics', help='Post sensor data to discrete topics instead of one JSON payload.', type=bool, default=False)

    args = parser.parse_args()

    print(f'\n\tSerial: {args.serial_port} -> MQTT: {args.client_id}@{args.mqtt_address}:{args.mqtt_port}/{args.topic}\n')

    ser = None  # global to main

    def parseLine(line, mqtt_client):
        pattern_found = False
        for pattern in (PATTERN_TEMP_ACTIVE, PATTERN_TEMP_IDLE, PATTERN_PROGRESS):

            res = pattern.match(line)

            if res:
                pattern_found = True
                if args.discrete_topics:
                    for name, value in res.groupdict().items():
                        mqtt_client.publish(f'{args.topic}/{PATTERN_TOPICS[pattern]}/{name}', value)
                else:
                    mqtt_client.publish(f'{args.topic}/{PATTERN_TOPICS[pattern]}', dumps(res.groupdict()))
                    print('.', end='')
                    sys.stdout.flush()

                mqtt_client.loop_start()

        if not pattern_found:
            print(f'> {line.strip()}')

    # send payload as GCODE to the printer when something arrives on topic/gcode
    def on_message(client, obj, msg):
        gcode = f"{msg.payload.decode('utf-8')}\n"
        print(f'\n< {gcode}')
        ser.write(bytearray(gcode, 'utf-8'))

    mqtt_client = mqtt.Client(args.client_id)

    if args.mqtt_username:
        mqtt_client.username_pw_set(args.mqtt_username, args.mqtt_password)
    mqtt_client.on_message = on_message
    mqtt_client.connect(args.mqtt_address, args.mqtt_port)
    mqtt_client.subscribe(f'{args.topic}/gcode', 0)
    mqtt_client.loop_start()

    # try to connect to the MQTT server
    for i in range(30):  # try for 3 seconds
        if mqtt_client.is_connected():
            break
        print('.', end='')
        sys.stdout.flush()
        time.sleep(0.1)

    if not mqtt_client.is_connected():
        sys.exit(f'\nCould not connect to the MQTT server at {args.mqtt_address}:{args.mqtt_port}, please check your parameters.')

    while True:
        try:
            with serial.Serial(args.serial_port, PRUSA_BAUDRATE, timeout=5) as ser:  # timeout is here so the MQTT loop get's called when no serial data is waiting
                while True:
                    mqtt_client.loop_start()
                    line = ser.readline().decode('utf-8')
                    if(line == ''):
                        continue  # timeout produces empty lines
                    if PATTERN_START.match(line):  # the printer does not recognise commands before that line
                        print('\n------ Printer starting ------\n')
                        ser.write(bytearray(f'M155 S{args.check_interval}\n', 'utf-8'))
                    elif PATTERN_END.match(line):
                        print('\n------ Printer shutdown ------\n')
                    else:
                        parseLine(line, mqtt_client)
        except Exception as err:
            print(err)


if __name__ == '__main__':
    main()
