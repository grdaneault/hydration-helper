#include "FastLED.h"
#include "lights/patterns/solid_pattern.h"

SolidLightPattern::SolidLightPattern(struct CHSV color)
{
    this->base_color = color;
}

SolidLightPattern::SolidLightPattern(struct CRGB color)
{
    this->base_color = rgb2hsv_approximate(color);
}

SolidLightPattern::~SolidLightPattern() {}

void SolidLightPattern::initialize(LightRing *ring)
{
    ring->fill_color(this->base_color);
}

void SolidLightPattern::update(LightRing *ring) {}