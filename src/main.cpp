#include <Arduino.h>

#include "service_instances.h"
#include "mqtt_connection.h"

#include "FastLED.h"
#include "lights/pattern_manager.h"

void setup()
{
    Serial.begin(115200);

    scale.init();

    ring.set_brightness(128);
    pattern_manager.set_pattern(PredefinedPatterns::PULSE_WHITE);

    initialize_network();

    Serial.println("Booted");
}

void loop()
{
    if (scale.is_offset_too_great())
    {
        Serial.println("Scale not empty when initialized. Retry tare");
        pattern_manager.set_pattern(PredefinedPatterns::SOLID_RED);
        scale.tare();
    }

    EVERY_N_MILLIS(100)
    {
        scale.take_sample();
    }

    EVERY_N_MILLISECONDS(500)
    {
        float weight = scale.current_value();
        send_weight(weight);
    }

    EVERY_N_MILLISECONDS(25)
    {
        pattern_manager.draw();
    }
}