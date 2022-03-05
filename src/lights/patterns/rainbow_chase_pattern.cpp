#include "FastLED.h"
#include "lights/patterns/rainbow_chase_pattern.h"

RainbowChaseLightPattern::~RainbowChaseLightPattern() {}

void RainbowChaseLightPattern::initialize(LightRing *ring)
{
    this->current_hue = 0;
    this->current_led = 0;
    ring->clear();
}

void RainbowChaseLightPattern::update(LightRing *ring)
{
    // Turn off previous LED and advance to the next
    ring->set_led(this->current_led++, CHSV(0, 0, 0));

    // Handle wraparound (if needed)
    if (this->current_led == ring->get_num_leds())
    {
        this->current_led = 0;
        this->current_hue += 10;
    }

    // Turn on current LED
    ring->set_led(this->current_led, CHSV(this->current_hue, 255, 255));
}