import logging

import paho.mqtt.client as mqtt

from config import Config, Patterns

logger = logging.getLogger(__name__)


class DataHandler:
    def __init__(self, mqtt_client: mqtt.Client):
        self.mqtt_client = mqtt_client
        self.last_value = float(-100)
        self.last_real_value = float(0)
        self.is_changing = False
        self.is_empty = False

    def record_weight(self, value: str):
        logger.debug(f"Got new weight: {value}")

        if self.is_weight_changing_state(value):
            self.handle_weight_changing_state()
            return

        weight = round(float(value), 5)

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
            logger.info(f"Weight Received: changing from empty to filled")
            self.set_pattern(Patterns.PULSE_GREEN)
        else:
            logger.info(f"Weight Received: changing from filled to empty")
            self.set_pattern(Patterns.OFF)

    def is_weight_same_as_last_value(self, value):
        """
        Check if the received value is +/- the same as the last one
        :param value: New value from the scale
        :return: True if the scale reports the same value as last time (within 1 gram)
        """
        return abs(value - self.last_value) < 1

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
        return abs(value) < 2

    def handle_weight_empty(self, weight):
        logger.info(f"Weight Received: empty ({weight}")
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
        else:
            # new value is more than old value - that means a refill!
            logger.info(f"Weight Received: refilled to {value} grams")
            self.set_pattern(Patterns.OFF)

        self.last_real_value = value
        self.is_changing = False
        self.is_empty = False

    def set_pattern(self, new_pattern: str):
        logger.debug(f"Sending Message: set the pattern to {new_pattern}")
        self.mqtt_client.publish(Config.MQTT_CHANNEL_PATTERN, payload=new_pattern, qos=0, retain=False)
