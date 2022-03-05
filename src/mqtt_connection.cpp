#include <WiFi.h>
extern "C"
{
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"
}
#include <AsyncMqttClient.h>

#include "secrets.h"
#include "service_instances.h"
#include "mqtt_connection.h"
#include "lights/pattern_manager.h"

AsyncMqttClient mqttClient;
TimerHandle_t mqttReconnectTimer;
TimerHandle_t wifiReconnectTimer;

void connect_to_wifi()
{
    Serial.println("Connecting to wifi");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void connect_to_mqtt()
{
    Serial.println("Connecting to mqtt server");
    mqttClient.connect();
}

void handle_mqtt_connect(bool sessionPresent)
{
    mqttClient.subscribe(MQTT_CHANNEL_BRIGHTNESS, 2);
    mqttClient.subscribe(MQTT_CHANNEL_PATTERN, 2);
    mqttClient.subscribe(MQTT_CHANNEL_TARE, 2);
}

void handle_wifi_event(WiFiEvent_t event)
{
    Serial.printf("[WiFi-event] event: %d\n", event);
    switch (event)
    {
    case SYSTEM_EVENT_STA_GOT_IP:
        Serial.print("WiFi connected. IP Address: ");
        Serial.println(WiFi.localIP());
        pattern_manager.set_pattern(PredefinedPatterns::SOLID_WHITE);
        connect_to_mqtt();
        break;
    case SYSTEM_EVENT_STA_DISCONNECTED:
        Serial.println("WiFi lost connection");
        xTimerStop(mqttReconnectTimer, 0); // ensure we don't reconnect to MQTT while reconnecting to Wi-Fi
        xTimerStart(wifiReconnectTimer, 0);
        pattern_manager.set_pattern(PredefinedPatterns::PULSE_WHITE);
        break;
    }
}

void handle_brightness_message(uint8_t new_brightness)
{
    Serial.print("Got brightness message: ");
    Serial.println(new_brightness);
    ring.set_brightness(new_brightness);
}

void handle_pattern_message(PredefinedPatterns new_pattern)
{
    Serial.print("Got pattern message: ");
    Serial.println(new_pattern);
    pattern_manager.set_pattern(new_pattern);
}

void handle_tare_message()
{
    Serial.println("Got tare message.");
    scale.tare();
}

void handle_mqtt_message(char *topic, char *payload, AsyncMqttClientMessageProperties properties, size_t len, size_t index, size_t total)
{
    if (strncmp(MQTT_CHANNEL_BRIGHTNESS, topic, 28) == 0)
    {
        handle_brightness_message(atoi(payload));
    }
    else if (strncmp(MQTT_CHANNEL_PATTERN, topic, 25) == 0)
    {
        handle_pattern_message((PredefinedPatterns)atoi(payload));
    }
    else if (strncmp(MQTT_CHANNEL_TARE, topic, 22) == 0)
    {
        handle_tare_message();
    }
    else
    {
        Serial.print("Unexpected topic received: ");
        Serial.println(topic);
    }
}

void initialize_network()
{
    mqttReconnectTimer = xTimerCreate("mqttTimer", pdMS_TO_TICKS(2000), pdFALSE, (void *)0, reinterpret_cast<TimerCallbackFunction_t>(connect_to_mqtt));
    wifiReconnectTimer = xTimerCreate("wifiTimer", pdMS_TO_TICKS(2000), pdFALSE, (void *)0, reinterpret_cast<TimerCallbackFunction_t>(connect_to_wifi));
    WiFi.onEvent(handle_wifi_event);

    mqttClient.onConnect(handle_mqtt_connect);
    // mqttClient.onDisconnect(onMqttDisconnect);
    // mqttClient.onSubscribe(onMqttSubscribe);
    // mqttClient.onUnsubscribe(onMqttUnsubscribe);
    mqttClient.onMessage(handle_mqtt_message);
    // mqttClient.onPublish(onMqttPublish);
    mqttClient.setCredentials(MQTT_USER, MQTT_PASSWORD);
    mqttClient.setServer(MQTT_HOSTNAME, 1883);

    connect_to_wifi();
}

char buffer[10];

void send_weight(float weight)
{
    snprintf(buffer, 10, "%f", weight);
    mqttClient.publish("hydration-helper/weight", 0, false, buffer);
    // Serial.println("Sent weight via mqtt");
}
