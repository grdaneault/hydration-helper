#ifndef MQTT_HEADER_GUARD
#define MQTT_HEADER_GUARD

#define MQTT_CHANNEL_BRIGHTNESS "hydration-helper/brightness"
#define MQTT_CHANNEL_PATTERN "hydration-helper/pattern"
#define MQTT_CHANNEL_TARE "hydration-helper/tare"

void initialize_network();

void send_weight(float value);

#endif