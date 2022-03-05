#ifndef LED_RING_HEADER_GUARD
#define LED_RING_HEADER_GUARD

#include "FastLED.h"

#define NUM_LEDS 42
#define LED_TYPE WS2812
#define COLOR_ORDER GRB
#define LED_DATA_PIN 27

class LightRing
{

public:
  LightRing();
  ~LightRing();

  void set_brightness(uint8_t brightness);

  void clear();
  void fill_color(CRGB color);
  void fill_color(CHSV color);
  void set_led(uint8_t led, CHSV color);

  uint8_t get_num_leds();

  void update();

private:
  CHSV adjust_brightness(struct CHSV color);
  CHSV adjust_brightness(struct CRGB color);
  uint8_t num_leds;
  struct CRGB *leds;
  bool needs_render;
  uint8_t brightness;
};

#endif
