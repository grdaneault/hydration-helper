#ifndef RAINBOW_CHASE_PATTERN_HEADER_GUARD
#define RAINBOW_CHASE_PATTERN_HEADER_GUARD

#include "lights/light_ring.h"
#include "lights/patterns/light_pattern.h"

class RainbowChaseLightPattern : public LightPattern
{
public:
  virtual ~RainbowChaseLightPattern();
  virtual void initialize(LightRing *ring);
  virtual void update(LightRing *ring);

private:
  uint8_t current_led;
  uint8_t current_hue;
};

#endif