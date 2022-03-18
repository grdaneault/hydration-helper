#include "lights/patterns/color_cycle_pattern.h"

ColorCycleLightPattern::ColorCycleLightPattern(struct ColorPhase *steps, uint8_t num_steps) {
    this->steps = steps;
    this->num_steps = num_steps;
}

ColorCycleLightPattern::~ColorCycleLightPattern() {}

void ColorCycleLightPattern::initialize(LightRing *ring) {
    this->current_step = 0;
    this->ticks_in_step = 0;
    ring->fill_color(this->steps[this->current_step].color);
}

void ColorCycleLightPattern::update(LightRing *ring) {
    if (this->ticks_in_step >= this->steps[this->current_step].ticks) {
        this->ticks_in_step = 0;
        this->current_step++;
        this->current_step %= this->num_steps;
        ring->fill_color(this->steps[this->current_step].color);
    } else {
        this->ticks_in_step++;
    }
}