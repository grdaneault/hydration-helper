#ifndef LIGHT_PATTERN_HEADER_GUARD
#define LIGHT_PATTERN_HEADER_GUARD

#include "FastLED.h"
#include "lights/light_ring.h"

class LightPattern
{
public:
  LightPattern();
  virtual ~LightPattern();
  virtual void initialize(LightRing *ring) = 0;
  virtual void update(LightRing *ring) = 0;
};

#endif