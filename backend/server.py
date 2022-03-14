import logging.config
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient

from config import Config
from data_handler import DataHandler

logger = logging.getLogger(__name__)
logging.config.fileConfig('logging_config.ini', disable_existing_loggers=False)


mqtt_client = mqtt.Client()
influx_client = InfluxDBClient(url=Config.INFLUX_URL, token=Config.INFLUX_TOKEN, org=Config.INFLUX_ORG)

data = DataHandler(mqtt_client, influx_client)


def on_connect(client: mqtt.Client, userdata, flags: dict, rc: int):
    logger.info(f"Connected to MQTT server. Result Code: {rc}")

    client.subscribe(Config.MQTT_CHANNEL_WEIGHT)


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    logger.debug(f"Topic {msg.topic}: {msg.payload}")

    if msg.topic == Config.MQTT_CHANNEL_WEIGHT:
        data.record_weight(msg.payload.decode('ascii'))


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.username_pw_set(Config.MQTT_USER, Config.MQTT_PASS)
mqtt_client.connect(Config.MQTT_HOST, Config.MQTT_PORT)

mqtt_client.loop_forever()
