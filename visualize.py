# visualize.py
"""
Quick–look plot of the GW150914 signal.

1. Downloads a 256 s Hanford (H1) strain segment centred on the event.
2. Crops to ±2 s for visual clarity.
3. Plots strain versus time.

Edit the USER PARAMS block to change GPS time, detector, or crop width.
"""

from matplotlib import pyplot as plt
from agents.fetch_validate import download

# ───────── USER PARAMS ───────── #
gps_event = 1126259462          # GW150914
detector = "H1"                 # use "L1", "V1", etc. for others
half_window = 128               # total segment = 2 × this
crop_width = 2                  # seconds plotted around the event
# ─────────────────────────────── #

# 1. Fetch & validate strain data
strain = download(detector, gps_event, window=half_window)

# 2. Zoom to small segment around event
strain_zoom = strain.crop(gps_event - crop_width, gps_event + crop_width)

# 3. Plot
plot = strain_zoom.plot()
ax = plot.gca()
ax.set_title(f"{detector} strain – GW150914")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Strain")

plt.show()