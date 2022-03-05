#ifndef PULSE_PATTERN_HEADER_GUARD
#define PULSE_PATTERN_HEADER_GUARD

#include "FastLED.h"
#include "lights/light_ring.h"
#include "lights/patterns/solid_pattern.h"

class PulseLightPattern : public SolidLightPattern
{
public:
  PulseLightPattern(struct CHSV color);
  PulseLightPattern(struct CRGB color);
  virtual ~PulseLightPattern();

  virtual void initialize(LightRing *ring);
  virtual void update(LightRing *ring);

private:
  uint8_t frame;
};

#endif