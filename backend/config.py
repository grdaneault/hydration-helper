import os


class Config:
    MQTT_HOST = "hydration-helper.home.greggernaut.com"
    MQTT_PORT = 1883

    MQTT_USER = os.getenv("MQTT_USER")
    MQTT_PASS = os.getenv("MQTT_PASS")

    MQTT_CHANNEL_WEIGHT = "hydration-helper/weight"
    MQTT_CHANNEL_BRIGHTNESS = "hydration-helper/brightness"
    MQTT_CHANNEL_PATTERN = "hydration-helper/pattern"
    MQTT_CHANNEL_TARE = "hydration-helper/tare"

    INFLUX_URL = "https://monitoring.home.greggernaut.com"
    INFLUX_ORG = "greggernet"
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

    INFLUX_BUCKET_LT = "hydration"
    INFLUX_BUCKET_ST = "hydration-short-term"
    INFLUX_METRIC_DRANK = "hydration.drank"
    INFLUX_METRIC_SCALE = "scale.weight"


class Patterns:
    OFF = '0'
    SOLID_WHITE = '1'
    SOLID_RED = '2'
    SOLID_GREEN = '3'
    SOLID_LIME = '4'
    SOLID_BLUE = '5'
    PULSE_WHITE = '6'
    PULSE_RED = '7'
    PULSE_GREEN = '8'
    PULSE_LIME = '9'
    PULSE_BLUE = '10'
    CYCLE_RED_ORANGE = '11'
    RAINBOW_CHASE = '12'
