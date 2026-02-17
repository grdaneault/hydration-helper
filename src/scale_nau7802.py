"""
NAU7802 load cell scale driver for CircuitPython.
I2C address 0x2a, 1 active channel. Converts raw readings to grams.
Returns a value from read_grams() only when a configurable number of raw
readings are within a configurable limit (stable); otherwise returns None (non-blocking).
"""

from cedargrove_nau7802 import NAU7802
from config import (
    RAW_TO_GRAM,
    SCALE_STABILITY_SAMPLES,
    SCALE_STABILITY_LIMIT_RAW,
)

class ScaleNAU7802:
    """
    Wrapper for NAU7802 24-bit ADC: tare and non-blocking read in grams.
    Averages a configurable number of raw readings and returns only when
    they are all within a configurable limit (stable); otherwise returns None.
    """

    def __init__(self, i2c, address=0x2A, active_channels=1):
        self._nau = NAU7802(i2c, address=address, active_channels=active_channels)
        if not self._nau.enable(True):
            raise RuntimeError("NAU7802 enable failed")
        self._gram_factor = RAW_TO_GRAM
        self._nau.channel = 1
        # Circular buffer: fixed size, no resizing
        self._buffer = [10 * SCALE_STABILITY_LIMIT_RAW] * SCALE_STABILITY_SAMPLES
        self._write_index = 0

    def tare(self):
        """Zero the scale. Call when scale is empty."""
        self._nau.calibrate("INTERNAL")
        self._nau.calibrate("OFFSET")
        for i in range(SCALE_STABILITY_SAMPLES):
            self._buffer[i] = 10 * SCALE_STABILITY_LIMIT_RAW
        self._write_index = 0

    def available(self):
        """True when a new sample is ready (non-blocking)."""
        return self._nau.available()

    def read_raw_blocking(self):
        """Read one raw sample. Block until a sample is ready."""
        while not self.available():
            pass
        return self._nau.read()

    def read_raw(self):
        """Read one raw sample. Call only when available() is True."""
        return self._nau.read()

    def read_grams(self):
        """
        Return weight in grams when the last SCALE_STABILITY_SAMPLES readings
        are stable (range <= limit). Reported value is the mean of those same
        samples. Otherwise returns None (non-blocking).
        """
        if not self.available():
            return None
        raw = self.read_raw()
        self._buffer[self._write_index] = raw
        self._write_index = (self._write_index + 1) % SCALE_STABILITY_SAMPLES
        hi, lo, total = self._buffer[0], self._buffer[0], self._buffer[0]
        for i in range(1, SCALE_STABILITY_SAMPLES):
            if self._buffer[i] > hi:
                hi = self._buffer[i]
            if self._buffer[i] < lo:
                lo = self._buffer[i]
            total += self._buffer[i]

        if hi - lo > SCALE_STABILITY_LIMIT_RAW:
            return None

        mean_raw = total / SCALE_STABILITY_SAMPLES
        return int(round(self._gram_factor * mean_raw))
