import logging
import time

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from config import Config, Patterns

logger = logging.getLogger(__name__)

SECONDS_BEFORE_WARNING = 60 * 30


class DataHandler:
    def __init__(self, mqtt_client: mqtt.Client, influx_client: InfluxDBClient):
        self.mqtt_client = mqtt_client
        self.influx_client = influx_client
        self.influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        self.influx_query_api = influx_client.query_api()
        self.last_value = float(-100)
        self.last_real_value = float(0)
        self.is_changing = False
        self.is_empty = False

        self.current_effect = 0
        self.last_effect_time = time.time()
        self.drink_warning_count = 0
        self.last_drink_time = time.time()
        self.last_drink_warning_time = time.time()

    def record_weight(self, value: str):
        logger.debug(f"Got new weight: {value}")

        if self.needs_hydration_reminder():
            self.handle_hydration_reminder()
        if self.current_effect != Patterns.OFF and time.time() - self.last_effect_time > 5:
            self.set_pattern(Patterns.OFF)

        if self.is_weight_changing_state(value):
            self.handle_weight_changing_state()
            return

        weight = round(float(value), 2)
        self.publish_raw_weight_metric(weight)

        if self.is_weight_same_as_last_value(weight):
            if self.is_changing and self.is_weight_empty(weight):
                self.handle_weight_empty(weight)
            else:
                logger.debug(f"No change in weight ({self.last_value} -> {weight})")

        elif self.is_weight_invalid(weight):
            self.handle_weight_invalid()

        elif self.is_weight_empty(weight):
            self.handle_weight_empty(weight)
        else:
            self.handle_weight_occupied(weight)

        self.last_value = weight

    @staticmethod
    def is_weight_changing_state(value):
        """
        Check if the received value indicates that the weight is currently changing
        :param value: New value from the scale
        :return: True if the scale reports the current weight is changing, False otherwise
        """
        return value == "changing"

    def handle_weight_changing_state(self):
        """
        Update the pattern
        :return:
        """
        if self.is_changing:
            # We're already in the changing state, nothing to do
            return

        self.is_changing = True
        if self.is_empty:
            logger.debug(f"Weight Received: changing from empty to filled")
        else:
            logger.debug(f"Weight Received: changing from filled to empty")

    def is_weight_same_as_last_value(self, value):
        """
        Check if the received value is +/- the same as the last one
        :param value: New value from the scale
        :return: True if the scale reports the same value as last time (within 1 gram)
        """
        return abs(value - self.last_value) < 2

    @staticmethod
    def is_weight_invalid(value):
        """
        Check if the received value is invalid (aka negative)
        This indicates that we probably need to re-tare the scale
        :param value: New value from the scale
        :return: True if the scale reports the current weight is invalid, False otherwise
        """
        return value < -1

    def handle_weight_invalid(self):
        logger.info("Sending Message: tare scale")
        self.mqtt_client.publish(Config.MQTT_CHANNEL_TARE, qos=0, retain=False)

    @staticmethod
    def is_weight_empty(value):
        """
        Check if the received value indicates the scale is empty
        :param value: New value from the scale
        :return: True if the scale reports the scale is empty
        """
        return abs(value) < 5

    def handle_weight_empty(self, weight):
        logger.info(f"Weight Received: empty ({weight})")
        self.set_pattern(Patterns.OFF)
        self.is_empty = True
        self.is_changing = False

    def handle_weight_occupied(self, value):
        amount_drank = round(self.last_real_value - value, 2)

        if abs(amount_drank) < 2:
            # new value is basically the same as the old one, assume no drink
            logger.info(f"Weight Received: same as last time (new: {value}, last: {self.last_real_value})")
            self.set_pattern(Patterns.OFF)
        elif amount_drank > 0:
            # new value is less than old value - that means we drank!
            logger.info(f"Weight Received: drank {amount_drank} grams! (current: {value})")
            self.set_pattern(Patterns.PULSE_GREEN)
            self.publish_clean_weight_metric(value, drank=amount_drank)
            self.last_drink_time = time.time()
            self.last_drink_warning_time = self.last_drink_time
            self.drink_warning_count = 0
        else:
            # new value is more than old value - that means a refill!
            logger.info(f"Weight Received: refilled to {value} grams")
            self.set_pattern(Patterns.PULSE_BLUE)
            self.publish_clean_weight_metric(value, refill=-amount_drank)

        self.last_real_value = value
        self.is_changing = False
        self.is_empty = False

    def publish_raw_weight_metric(self, value):
        point = Point(Config.INFLUX_METRIC_SCALE).field("weight", value)
        try:
            self.influx_write_api.write(bucket=Config.INFLUX_BUCKET_ST, record=point)
        except Exception:
            logger.exception("Error writing point to influx")

    def publish_clean_weight_metric(self, value, drank=None, refill=None):

        point = Point(Config.INFLUX_METRIC_DRANK).field("weight", value)

        if drank is not None:
            point = point.field("drank", drank)

        if refill is not None:
            point = point.field("refill", refill)

        try:
            self.influx_write_api.write(bucket=Config.INFLUX_BUCKET_LT, record=point)
        except Exception:
            logger.exception("Error writing point to influx")

    def needs_hydration_reminder(self):
        now = time.time()
        return now - self.last_drink_warning_time > SECONDS_BEFORE_WARNING

    def handle_hydration_reminder(self):
        now = time.time()
        logger.warning(f"No hydration in {round(now - self.last_drink_time, 0)} seconds. Sending warning {self.drink_warning_count}.")
        self.set_pattern(Patterns.CYCLE_RED_ORANGE)
        self.last_drink_warning_time = now
        self.drink_warning_count += 1

    def set_pattern(self, new_pattern: str):
        logger.info(f"Sending Message: set the pattern to {new_pattern}")
        self.mqtt_client.publish(Config.MQTT_CHANNEL_PATTERN, payload=new_pattern, qos=1, retain=True)
        self.current_effect = new_pattern
        self.last_effect_time = time.time()
