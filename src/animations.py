"""
Non-blocking LED animations: solid, pulse (blue/green/red with level), sparkle, off.
One step() per call; no sleep. Uses a precomputed pulse brightness table (120 frames).
Animations are configurable structs: PulseAnimation, SparkleAnimation, SolidAnimation, BlankAnimation.
"""
import math

# 120-frame pulse (same shape as C pulse_pattern.cpp): ramp up, hold, ramp down
PULSE_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 3, 8, 15, 27, 43, 65, 92, 127, 162, 189, 211, 227, 239, 246, 251, 253, 254, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 254, 253, 251, 246, 239, 227, 211, 189, 162, 127, 92, 65, 43, 27, 15, 8, 3, 1, 0,
]
NUM_PULSE_FRAMES = len(PULSE_TABLE)
FPS = 60  # used to convert sparkle duration (seconds) to frames

# Colors (R, G, B) for Neopixel
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_OFF = (0, 0, 0)


def _scale_brightness(rgb, factor):
    """Factor 0.0..1.0. Returns (r,g,b) tuple."""
    return (
        int(rgb[0] * factor),
        int(rgb[1] * factor),
        int(rgb[2] * factor),
    )


# --- Animation parameter structs ---

class SolidAnimation:
    """Solid color, does not end."""

    def __init__(self, color):
        self.color = color

    def __eq__(self, other):
        return isinstance(other, SolidAnimation) and self.color == other.color

    def animate(self, frame, num_pixels, pixels):
        pixels.fill(self.color)
        pixels.show()
        return True


class PulseAnimation:
    """Pulse: color, number of pulse cycles, brightness scale 0.0..1.0."""

    def __init__(self, color, pulse_count, brightness):
        self.color = color
        self.pulse_count = pulse_count
        self.brightness = brightness

    def __eq__(self, other):
        if not isinstance(other, PulseAnimation):
            return False
        return (
                self.color == other.color
                and self.pulse_count == other.pulse_count
                and self.brightness == other.brightness
        )

    def animate(self, frame, num_pixels, pixels):
        idx = frame % NUM_PULSE_FRAMES
        v = PULSE_TABLE[idx] / 255.0 * self.brightness
        r, g, b = _scale_brightness(self.color, v)
        pixels.fill((r, g, b))
        pixels.show()
        return frame < NUM_PULSE_FRAMES * self.pulse_count


def _lerp_rgb(color1, color2, t):
    """Blend color1 and color2; t in 0..1."""
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t),
    )


def _pixel_phase(i, frame, speed_scale=0.018):
    """
    Deterministic phase 0..1 for pixel i at frame, with per-pixel speed and offset.
    Speed and offset derived from index so each pixel fades at a different rate.
    """
    # Per-pixel speed in a range (e.g. 0.2–1.0) so some pixels cycle slower
    speed = 0.2 + 0.8 * ((i * 7919 + 1) % 1000) / 1000
    # Per-pixel offset so they don't all start in sync
    offset = ((i * 1237) % 1000) / 1000
    phase = (frame * speed * speed_scale + offset) % 1.0
    return phase


class SparkleAnimation:
    """Sparkle: pixels smoothly fade between two colors at different rates. Duration in seconds."""

    def __init__(self, color1, color2, duration):
        self.color1 = color1
        self.color2 = color2
        self.duration = duration

    def __eq__(self, other):
        if not isinstance(other, SparkleAnimation):
            return False
        return (
                self.color1 == other.color1
                and self.color2 == other.color2
                and self.duration == other.duration
        )

    def animate(self, frame, num_pixels, pixels):
        total_frames = int(self.duration * FPS)
        fade_frames = max(1, int(total_frames * 0.15))  # 15% of duration for fade in/out
        if frame < fade_frames:
            brightness = frame / fade_frames
        elif frame >= total_frames - fade_frames:
            brightness = (total_frames - frame) / fade_frames
        else:
            brightness = 1.0

        for i in range(num_pixels):
            phase = _pixel_phase(i, frame)
            # Smooth 0→1→0 over one cycle (sine)
            t = (math.sin(phase * 2 * math.pi) + 1) / 2
            color = _lerp_rgb(self.color1, self.color2, t)
            pixels[i] = _scale_brightness(color, brightness)
        pixels.show()
        return frame < total_frames




# --- Named animation constants (replicate existing behavior) ---
SOLID_BLUE = SolidAnimation(COLOR_BLUE)
SOLID_RED = SolidAnimation(COLOR_RED)
GREEN_PULSE = PulseAnimation(COLOR_GREEN, 1, 1.0)
BLUE_PULSE = PulseAnimation(COLOR_BLUE, 1, 1.0)
LIGHT_BLUE_PULSE = PulseAnimation(COLOR_BLUE, 1, 0.25)
SPARKLE = SparkleAnimation(COLOR_GREEN, COLOR_BLUE, 3)
SPARKLE_RED = SparkleAnimation(COLOR_RED, COLOR_YELLOW, 3)

RED_PULSE_1 = PulseAnimation(COLOR_RED, 1, 0.25)
RED_PULSE_2 = PulseAnimation(COLOR_RED, 1, 0.5)
RED_PULSE_3 = PulseAnimation(COLOR_RED, 1, 0.75)
RED_PULSE_4 = PulseAnimation(COLOR_RED, 1, 1.0)
RED_PULSE_LEVELS = (SPARKLE_RED, RED_PULSE_1, RED_PULSE_2, RED_PULSE_3, RED_PULSE_4)

BLANK = None


class AnimationController:
    def __init__(self, pixels, num_pixels):
        self.pixels = pixels
        self.num_pixels = num_pixels
        self._frame = 0
        self._current_anim = None

    def set_animation(self, animation):
        if animation is None and self._current_anim is None:
            return

        self._current_anim = animation
        self._frame = 0

        if not isinstance(animation, (SolidAnimation, PulseAnimation, SparkleAnimation)):
            self._current_anim = None
            self.pixels.fill(COLOR_OFF)
            self.pixels.show()
            print("set_animation: None")
        else:
            print(f"set_animation: {type(animation)}")

    def step(self):
        """
        Advance one frame for the current animation.
        Writes to self.pixels; caller calls pixels.show() after.
        Returns True if a frame was shown, False when the animation has ended (pulse/sparkle).
        """

        if self._current_anim is None:
            return False

        continuing = self._current_anim.animate(self._frame, self.num_pixels, self.pixels)
        self.pixels.show()
        if continuing:
            self._frame += 1
        else:
            self.set_animation(None)
        return continuing
