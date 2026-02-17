# Hydration helper configuration constants (tunable)

# Scale: tare when weight <= this (grams)
NEAR_ZERO_G = 5

# Reminders: first red pulse after no consumption (minutes)
REMINDER_FIRST_MIN = 20

# Reminders: interval between subsequent red pulses (minutes)
REMINDER_INTERVAL_MIN = 5

# Idle: stop reminder animations after no consumption and scale empty (minutes)
IDLE_AFTER_MIN = 60

# Reminders: max escalation level (brightness/duration cap)
REMINDER_LEVEL_CAP = 5

# Min weight change (grams) to treat as "bottle filled" or "drank" (hysteresis)
GRAM_DELTA_HYSTERESIS = 5

# Raw to grams: multiply NAU7802 raw reading by this
RAW_TO_GRAM = 377 / 324400

# Scale stability: number of raw readings that must be within limit to consider stable; same window is averaged for the reported value
SCALE_STABILITY_SAMPLES = 4

# Scale stability: max allowed range (max - min) of those readings to consider stable
SCALE_STABILITY_LIMIT_RAW = 500

# NAU7802 I2C address
NAU7802_I2C_ADDRESS = 0x2A

# NAU7802 active channels
NAU7802_ACTIVE_CHANNELS = 1

# Neopixel count and pin (pin name string for board.A0 usage in code.py)
NUM_PIXELS = 44

# Post-tare green pulse duration (seconds) before entering monitoring
POST_TARE_PULSE_SEC = 4

# Tare delay (seconds) to prevent tare spamming
TARE_DELAY_SEC = 120