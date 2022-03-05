#include "lights/pattern_manager.h"
#include "lights/patterns/solid_pattern.h"
#include "lights/patterns/pulse_pattern.h"
#include "lights/patterns/rainbow_chase_pattern.h"

SolidLightPattern OFF_INST(CHSV(0, 0, 0));
SolidLightPattern SOLID_WHITE_INST(CHSV(0, 0, 255));
SolidLightPattern SOLID_RED_INST(CHSV(0, 255, 255));
SolidLightPattern SOLID_GREEN_INST(CHSV(115, 255, 255));
SolidLightPattern SOLID_LIME_INST(CHSV(90, 255, 255));
PulseLightPattern PULSE_WHITE_INST(CHSV(0, 0, 255));
PulseLightPattern PULSE_RED_INST(CHSV(0, 255, 255));
PulseLightPattern PULSE_GREEN_INST(CHSV(115, 255, 255));
RainbowChaseLightPattern RAINBOW_CHASE_INST;

PatternManager::PatternManager(LightRing *ring)
{
    this->ring = ring;

    this->patterns = (LightPattern **)malloc(sizeof(LightPattern *) * NUM_PATTERNS);
    this->patterns[PredefinedPatterns::OFF] = &OFF_INST;
    this->patterns[PredefinedPatterns::SOLID_WHITE] = &SOLID_WHITE_INST;
    this->patterns[PredefinedPatterns::SOLID_RED] = &SOLID_RED_INST;
    this->patterns[PredefinedPatterns::SOLID_GREEN] = &SOLID_GREEN_INST;
    this->patterns[PredefinedPatterns::SOLID_LIME] = &SOLID_LIME_INST;
    this->patterns[PredefinedPatterns::PULSE_WHITE] = &PULSE_WHITE_INST;
    this->patterns[PredefinedPatterns::PULSE_RED] = &PULSE_RED_INST;
    this->patterns[PredefinedPatterns::PULSE_GREEN] = &PULSE_GREEN_INST;
    this->patterns[PredefinedPatterns::RAINBOW_CHASE] = &RAINBOW_CHASE_INST;
}

PatternManager::~PatternManager()
{
    free(this->patterns);
}

void PatternManager::set_pattern(uint8_t pattern_id)
{
    this->current_pattern = pattern_id;
    // RAINBOW_CHASE_INST.initialize(this->ring);
    this->patterns[this->current_pattern]->initialize(this->ring);
}

void PatternManager::draw()
{
    this->patterns[this->current_pattern]->update(this->ring);
    // RAINBOW_CHASE_INST.update(this->ring);
    this->ring->update();
}
