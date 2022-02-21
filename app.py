from pickletools import int4
from re import match
from json import dumps
import serial

import paho.mqtt.client as mqtt

PRUSA_BAUDRATE = 115200

# 'T:26.1 /0.0 B:25.6 /0.0 T0:26.1 /0.0 @:0 B@:0 P:27.3 A:33.8' <- example status line
temp_status_pattern = r'T:(?P<extruder_actual>\d+\.\d) /(?P<extruder_target>\d+\.\d) B:(?P<bed_actual>\d+\.\d) /(?P<bed_target>\d+\.\d) T0:(\d+\.\d) /(\d+\.\d) @:(?P<hotend_power>\d+) B@:(?P<bed_power>\d+) P:(?P<pinda>\d+\.\d) A:(?P<ambient>\d+\.\d)'


def main(args):
    def parseLine(line, mqtt_client):
        res = match(temp_status_pattern, line)
        if res:
            if args.discrete_topics:
                for name, value in res.groupdict().items():
                    mqtt_client.publish(f'{args.topic}/{name}', value)
            else:
                mqtt_client.publish(f'{args.topic}', dumps(res.groupdict()))

            mqtt_client.loop_start()
        else:
            print(line.strip())

    mqtt_client = mqtt.Client(args.client_id)
    mqtt_client.connect(args.mqtt_address, args.mqtt_port)

    while True:
        try:
            with serial.Serial(args.serial_port, PRUSA_BAUDRATE, timeout=None) as ser:
                while True:
                    line = ser.readline().decode('utf-8')
                    if line == 'start\n':  # the printer does not recognise commands before that line
                        ser.write(b'M155 S4\n')
                    else:
                        parseLine(line, mqtt_client)
        except Exception as err:
            print(err)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Log temperature data from the USB port of a Prusa printer to an MQTT server.')
    parser.add_argument('--topic', help='Topic for the MQTT message.', default='prusa')
    parser.add_argument('--client_id', help='Distinct client ID for the MQTT connection.', default='prusa2mqtt')
    parser.add_argument('--serial_port', help='Path to the serial port device.', default='/dev/ttyACM0')
    parser.add_argument('--mqtt_address', help='Address for the MQTT connection.', default='localhost')
    parser.add_argument('--mqtt_port', help='Port for the MQTT connection.', type=int, default=1883)
    parser.add_argument('--discrete_topics', help='Post sensor data to discrete topics instead of one JSON payload.', type=bool, default=False)

    args = parser.parse_args()
    main(args)
