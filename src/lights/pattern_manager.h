#ifndef PATTERN_MANAGER_HEADER_GUARD
#define PATTERN_MANAGER_HEADER_GUARD

#include "lights/light_ring.h"
#include "lights/patterns/light_pattern.h"

#define NUM_PATTERNS 13

enum PredefinedPatterns
{
    OFF = 0,
    SOLID_WHITE,
    SOLID_RED,
    SOLID_GREEN,
    SOLID_LIME,
    SOLID_BLUE,
    PULSE_WHITE,
    PULSE_RED,
    PULSE_GREEN,
    PULSE_LIME,
    PULSE_BLUE,
    CYCLE_RED_ORANGE,
    RAINBOW_CHASE
};

class PatternManager
{
public:
    PatternManager(LightRing *ring);
    ~PatternManager();
    void set_pattern(uint8_t pattern_id);
    void set_brightness(uint8_t brightness);
    void draw();

private:
    LightRing *ring;
    LightPattern **patterns;
    uint8_t current_pattern;
};

#endif