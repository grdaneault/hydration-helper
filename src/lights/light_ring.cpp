#include "FastLED.h"
#include "lights/light_ring.h"

LightRing::LightRing()
{
    this->num_leds = NUM_LEDS;
    this->leds = (CRGB *)malloc(sizeof(CRGB) * this->num_leds);
    this->brightness = 255;
    this->needs_render = true;

    FastLED.addLeds<LED_TYPE, LED_DATA_PIN, COLOR_ORDER>(this->leds, this->num_leds);
}

LightRing::~LightRing()
{
    free(this->leds);
}

void LightRing::set_brightness(uint8_t brightness)
{
    this->brightness = brightness;
}

void LightRing::clear()
{
    FastLED.clear();
}

void LightRing::set_led(uint8_t led, CHSV color)
{
    this->needs_render = true;
    this->leds[led] = this->adjust_brightness(color);
}

uint8_t LightRing::get_num_leds()
{
    return this->num_leds;
}

void LightRing::update()
{
    if (this->needs_render)
    {
        FastLED.show();
        this->needs_render = false;
    }
}

void LightRing::fill_color(CHSV color)
{
    this->needs_render = true;
    CHSV brightness_adjusted = this->adjust_brightness(color);

    for (uint8_t led = 0; led < this->num_leds; led++)
    {
        this->leds[led] = brightness_adjusted;
    }
}

void LightRing::fill_color(CRGB color)
{
    this->fill_color(rgb2hsv_approximate(color));
}

struct CHSV LightRing::adjust_brightness(CHSV color)
{
    CHSV adjusted = CHSV(color);
    adjusted.value = (uint8_t)round(this->brightness / 255.0 * adjusted.value);
    return adjusted;
}

struct CHSV LightRing::adjust_brightness(CRGB color)
{
    return this->adjust_brightness(rgb2hsv_approximate(color));
}
