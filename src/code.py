"""
Hydration helper - CircuitPython entry point.
ESP32 QT Py, NAU7802 @ I2C 0x2a, 44 Neopixels on A0.
Startup: solid blue until tare -> green pulse -> monitoring loop.
Main loop: non-blocking scale read, hydration update, animation step, print (current_weight, total_water_consumed).
"""

import board
import time
import neopixel

from scale_nau7802 import ScaleNAU7802
from hydration import HydrationState, NS_PER_SEC
from animations import AnimationController, BLUE_PULSE, GREEN_PULSE, SOLID_RED

try:
    from config import (
        NAU7802_I2C_ADDRESS,
        NAU7802_ACTIVE_CHANNELS,
        NUM_PIXELS,
    )
except ImportError:
    NAU7802_I2C_ADDRESS = 0x2A
    NAU7802_ACTIVE_CHANNELS = 1
    NUM_PIXELS = 44

# --- Hardware init ---
i2c = board.STEMMA_I2C()
scale = ScaleNAU7802(i2c, address=NAU7802_I2C_ADDRESS, active_channels=NAU7802_ACTIVE_CHANNELS)
pixels = neopixel.NeoPixel(board.A0, NUM_PIXELS, brightness=0.3, auto_write=False)
anim = AnimationController(pixels, NUM_PIXELS)
hydration = HydrationState(anim)

# --- Startup: blue flash on boot then tare ---
anim.set_animation(BLUE_PULSE)
while anim.step():
    time.sleep(1 / 60)

# scale is "warm" idk if that really matters but seems fine for now.
# check that the scale isn't reporting too much weight already (might not be empty which will mess up all the math)
initial_value = scale.read_raw_blocking()
while initial_value > 500_000:
    print("scale not empty -- please remove weight for tare")
    anim.set_animation(SOLID_RED)
    anim.step()
    time.sleep(1)
    initial_value = scale.read_raw_blocking()




scale.tare()
anim.set_animation(GREEN_PULSE)
while anim.step():
    time.sleep(1 / 60)

last = (-1, 0, 0, 0, False)
last_anim = time.monotonic_ns()
anim_interval_ns = NS_PER_SEC // 60
while True:
    g = scale.read_grams()
    if g is not None:
        hydration.update(g)
        next = (g, hydration.current_weight, hydration.last_water_weight, hydration.total_water_consumed, hydration.pending_tare)
        if next[0] != last[0] or next[1] != last[1] or next[2] != last[2] or next[3] != last[3] or next[4] != last[4]:
            print(next)
            last = next

    if hydration.should_tare():
        scale.tare()
        hydration.report_tare()

    now_ns = time.monotonic_ns()
    if now_ns - last_anim > anim_interval_ns:
        last_anim = now_ns
        anim.step()

