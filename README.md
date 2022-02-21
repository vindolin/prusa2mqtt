# prusa2mqtt

Command line tool that parses the USB serial output of a Prusa printer and publishes the sensor values to an MQTT server.

```bash
prusa2mqtt --help
```

```
usage: prusa2mqtt [-h] [--topic TOPIC] [--client_id CLIENT_ID]
                     [--check_interval CHECK_INTERVAL]
                     [--serial_port SERIAL_PORT] [--mqtt_address MQTT_ADDRESS]
                     [--mqtt_port MQTT_PORT] [--mqtt_username MQTT_USERNAME]
                     [--mqtt_password MQTT_PASSWORD]
                     [--discrete_topics DISCRETE_TOPICS]

Log temperature data from the USB port of a Prusa printer to an MQTT server.

optional arguments:
  -h, --help            show this help message and exit
  --serial_port SERIAL_PORT
                        Path to the serial port device. (default: /dev/ttyACM0)
  --topic TOPIC         Topic for the MQTT message. (default: prusa)
  --client_id CLIENT_ID
                        Distinct client ID for the MQTT connection. (default: prusa2mqtt)
  --check_interval CHECK_INTERVAL
                        Interval in seconds for checking the temperatures. (default: 5)
  --serial_port SERIAL_PORT
                        Path to the serial port device.
  --mqtt_address MQTT_ADDRESS
                        Address for the MQTT connection. (default: localhost)
  --mqtt_port MQTT_PORT
                        Port for the MQTT connection. (default: 1883)
  --mqtt_username MQTT_USERNAME
                        User name for the MQTT connection. (default: None)
  --mqtt_password MQTT_PASSWORD
                        Password name for the MQTT connection. (default: None)
  --discrete_topics DISCRETE_TOPICS
                        Post sensor data to discrete topics instead of one JSON payload. (default: False)
```
