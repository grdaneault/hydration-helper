#include "lights/light_ring.h"
#include "lights/patterns/pulse_pattern.h"

#define NUM_PULSE_FRAMES 120
uint8_t PULSE_PATTERN[NUM_PULSE_FRAMES] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 8, 15, 27, 43, 65, 92, 127, 162, 189, 211, 227, 239, 246, 251, 253, 254, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 254, 253, 251, 246, 239, 227, 211, 189, 162, 127, 92, 65, 43, 27, 15, 8, 3, 1, 0};

PulseLightPattern::PulseLightPattern(struct CHSV color) : SolidLightPattern(color) {}
PulseLightPattern::PulseLightPattern(struct CRGB color) : SolidLightPattern(color) {}
PulseLightPattern::~PulseLightPattern() {}

void PulseLightPattern::initialize(LightRing *ring)
{
    this->base_color.value = 0;
    this->frame = 0;
    ring->fill_color(this->base_color);
}

void PulseLightPattern::update(LightRing *ring)
{
    this->base_color.value = PULSE_PATTERN[this->frame++];
    if (this->frame == NUM_PULSE_FRAMES)
    {
        this->frame = 0;
    }
    ring->fill_color(this->base_color);
}