#ifndef SOLID_PATTERN_HEADER_GUARD
#define SOLID_PATTERN_HEADER_GUARD

#include "FastLED.h"
#include "lights/light_ring.h"
#include "lights/patterns/light_pattern.h"

class SolidLightPattern : public LightPattern
{
public:
  SolidLightPattern(struct CHSV color);
  SolidLightPattern(struct CRGB color);
  virtual ~SolidLightPattern();
  virtual void initialize(LightRing *ring);
  virtual void update(LightRing *ring);

protected:
  CHSV base_color;
};

#endif