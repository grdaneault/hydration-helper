"""
Hydration state machine: weight rules, tare request, reminder timers, and current animation.
Uses time.monotonic_ns() for timers to avoid precision loss over long runtimes.
"""

import time

NS_PER_SEC = 1_000_000_000

from config import (
    NEAR_ZERO_G,
    FIRST_REMINDER_SEC,
    REMINDER_INTERVAL_SEC,
    IDLE_AFTER_SEC,
    GRAM_DELTA_HYSTERESIS,
    TARE_DELAY_SEC,
)

from animations import (
    RED_PULSE_LEVELS,
    SPARKLE,
    LIGHT_BLUE_PULSE,
)

# Convert minutes to nanoseconds for comparisons
reminder_first_ns = FIRST_REMINDER_SEC * NS_PER_SEC
reminder_interval_ns = REMINDER_INTERVAL_SEC * NS_PER_SEC
idle_after_ns = IDLE_AFTER_SEC * NS_PER_SEC


class HydrationState:
    """
    Tracks total_water_consumed, current_weight, previous_weight (grams, integer);
    last_consumption_time, last_reminder_time, reminder_level, idle.
    Exposes current_animation (+ optional level for red escalation) and should_tare().
    """

    def __init__(self, animation_controller):
        boot_time = time.monotonic_ns()
        self.total_water_consumed = 0
        self.current_weight = 0
        self.last_weight = 0
        self.last_water_weight = 0

        self.last_consumption_time = boot_time
        self.last_activity_time = boot_time
        self.idle = False

        self.last_reminder_time = boot_time
        self.reminder_level = 0

        self.pending_tare = False
        self.last_tare_time = None
        self.animation_controller = animation_controller

    def update(self, weight_grams):
        """
        Run state machine on new weight reading (grams, integer).
        Sets current_animation and sets pending_tare when appropriate.
        """
        now_ns = time.monotonic_ns()
        current_weight = weight_grams
        last_weight = self.current_weight
        self.current_weight = current_weight

        # Scale is empty
        if current_weight <= NEAR_ZERO_G:
            if last_weight > NEAR_ZERO_G:
                # Scale was not empty before, request tare
                self.pending_tare = True
                self.last_activity_time = now_ns
            else:
                # Scale was already empty, maybe send a hydration reminder
                self._maybe_reminder_or_idle(now_ns)
            return
        else:
            self.pending_tare = False
            self.last_tare_time = None

        # Bottle filled: weight increased beyond previous
        if current_weight >= self.last_water_weight + GRAM_DELTA_HYSTERESIS:
            self.last_water_weight = self.current_weight
            self.animation_controller.set_animation(LIGHT_BLUE_PULSE)
            self.last_activity_time = now_ns
            self.idle = False
            self._maybe_reminder_or_idle(now_ns)
            return

        # Drank: weight between 0 and previous (and decreased)
        if self.last_water_weight - self.current_weight > GRAM_DELTA_HYSTERESIS:
            drunk = self.last_water_weight - self.current_weight
            self.total_water_consumed += drunk
            self.last_water_weight = self.current_weight
            self.last_consumption_time = now_ns
            self.animation_controller.set_animation(SPARKLE)
            self.reminder_level = 0
            self.last_reminder_time = None
            self.idle = False
            return

        # No state change: maybe reminder or idle
        self._maybe_reminder_or_idle(now_ns)

    def _maybe_reminder_or_idle(self, now_ns):
        if self.idle:
            return

        last = self.last_consumption_time or 0
        idle_ns = now_ns - last

        if idle_ns >= idle_after_ns and self.current_weight <= NEAR_ZERO_G:
            # Scale has been empty and inactive for too long, enter idle mode
            self.idle = True
            self.animation_controller.set_animation(None)
            return

        if idle_ns <= reminder_first_ns:
            # Not enough time has passed since last consumption, don't send a reminder
            return

        if self.last_reminder_time is None or now_ns - self.last_reminder_time >= reminder_interval_ns:
            self.reminder_level = min(self.reminder_level + 1, len(RED_PULSE_LEVELS))
            self.last_reminder_time = now_ns
            idx = min(self.reminder_level - 1, len(RED_PULSE_LEVELS) - 1)
            self.animation_controller.set_animation(RED_PULSE_LEVELS[idx])

    def should_tare(self):
        """True when we should call scale.tare() (weight was near zero and we haven't cleared it yet)."""
        return self.pending_tare and (self.last_tare_time is None or self.last_tare_time + TARE_DELAY_SEC * NS_PER_SEC < time.monotonic_ns())

    def report_tare(self):
        """Call after performing tare so we don't tare again until next near-zero."""
        self.last_tare_time = time.monotonic_ns()
