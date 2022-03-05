#ifndef SCALE_HEADER_GUARD
#define SCALE_HEADER_GUARD

#include "HX711.h"

#define SCALE_DOUT_PIN 26
#define SCALE_SCK_PIN 25
#define SCALE_SAMPLE_BUFFER_SIZE 5

class Scale
{
public:
    Scale();
    virtual ~Scale();

    void init();
    bool is_offset_too_great();
    void tare();
    void take_sample();
    float current_value();

private:
    HX711 scale;
    float *sample_buffer;
    uint8_t current_sample;
};

#endif