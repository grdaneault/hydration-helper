#include <Arduino.h>
#include "scale.h"

Scale::Scale()
{
    this->sample_buffer = (float *)malloc(sizeof(float) * SCALE_SAMPLE_BUFFER_SIZE);
    this->current_sample = 0;
}

Scale::~Scale()
{
    free(this->sample_buffer);
}

void Scale::init()
{
    this->scale.begin(SCALE_DOUT_PIN, SCALE_SCK_PIN);
    this->scale.set_scale(692250.0f / 1430.0f);
    this->scale.tare();
}

void Scale::tare()
{
    this->scale.tare();
}

bool Scale::is_offset_too_great()
{
    return this->scale.get_offset() > 700000;
}

void Scale::take_sample()
{
    if (!this->scale.is_ready())
    {
        return;
    }
    this->sample_buffer[this->current_sample] = this->scale.read();
    this->current_sample += 1;
    this->current_sample %= SCALE_SAMPLE_BUFFER_SIZE;
}

float calculate_weight(long raw_value, long offset, float scale)
{
    return (raw_value - offset) / scale;
}

float Scale::current_value()
{
    float total = 0;
    for (uint8_t i = 0; i < SCALE_SAMPLE_BUFFER_SIZE; i++)
    {
        total += this->sample_buffer[i];
    }

    float avg = total / SCALE_SAMPLE_BUFFER_SIZE;

    long offset = this->scale.get_offset();
    long scale = this->scale.get_scale();

    float avg_weight = calculate_weight(avg, offset, scale);
    float last_weight = calculate_weight(this->sample_buffer[this->current_sample], offset, scale);

    float delta = avg_weight - last_weight;
    if (delta > 1 || delta < -1)
    {
        Serial.print("High delta: ");
        Serial.print(delta);
        Serial.print(" (avg: ");
        Serial.print(avg_weight);
        Serial.print(", last: ");
        Serial.print(last_weight);
        Serial.println(")");
        return 0;
    }

    return avg_weight;
}
