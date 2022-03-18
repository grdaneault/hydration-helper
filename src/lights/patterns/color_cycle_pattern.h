#ifndef COLOR_CYCLE_PATTERN_HEADER_GUARD
#define COLOR_CYCLE_PATTERN_HEADER_GUARD

#include "lights/light_ring.h"
#include "lights/patterns/light_pattern.h"

struct ColorPhase {
    struct CHSV color;
    uint8_t ticks; 
};

class ColorCycleLightPattern : public LightPattern
{
public:
    ColorCycleLightPattern(struct ColorPhase *steps, uint8_t num_steps);
    virtual ~ColorCycleLightPattern();
    virtual void initialize(LightRing *ring);
    virtual void update(LightRing *ring);

private:
    struct ColorPhase *steps;
    uint8_t num_steps;
    uint8_t current_step;
    uint8_t ticks_in_step;
};

#endif