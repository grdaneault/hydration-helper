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

def _elapsed_hhmmss_ns(ns):
    """Convert monotonic nanoseconds to elapsed time string hh:mm:ss."""
    s = ns // NS_PER_SEC
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return "{:02d}:{:02d}:{:02d}".format(h, m, s)



last_anim = time.monotonic_ns()
last_print_ns = time.monotonic_ns()
print_interval_ns = 5 * 60 * NS_PER_SEC  # 5 minutes
anim_interval_ns = NS_PER_SEC // 60
while True:
    g = scale.read_grams()
    if g is not None:
        state_changed = hydration.update(g)
        next_ = (g, hydration.current_weight, hydration.last_water_weight, hydration.total_water_consumed, hydration.pending_tare)
        now_ns = time.monotonic_ns()
        should_print = state_changed or (now_ns - last_print_ns >= print_interval_ns)
        if should_print:
            last_print_ns = now_ns
            ts = _elapsed_hhmmss_ns(now_ns)
            print(f"[{ts}] current weight: {g}g, total consumed: {hydration.total_water_consumed}g last known weight: {hydration.last_water_weight}g")

    if hydration.should_tare():
        scale.tare()
        hydration.report_tare()

    now_ns = time.monotonic_ns()
    if now_ns - last_anim > anim_interval_ns:
        last_anim = now_ns
        anim.step()

