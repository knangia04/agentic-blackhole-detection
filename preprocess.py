"""
Preprocessing module for gravitational wave strain data.

1. Bandpass filter the data to retain physical GW signal range (30–500 Hz).
2. Apply notch filters to remove known instrumental lines.
3. Whiten the data to flatten the noise spectrum.

This module assumes the input strain is a GWpy TimeSeries.
"""
from matplotlib import pyplot as plt
from agents.fetch_validate import download
from gwpy.timeseries import TimeSeries
from gwpy.signal.filter_design import bandpass, notch
from scipy.signal import welch
import numpy as np


def preprocess(strain: TimeSeries, low=30, high=500, notches=None, fftlength=4) -> TimeSeries:
    """
    Preprocess raw strain data.

    Parameters:
    - strain: GWpy TimeSeries object of raw strain data.
    - low: Low frequency cutoff for bandpass filter (Hz).
    - high: High frequency cutoff for bandpass filter (Hz).
    - notches: List of notch filter frequencies (Hz), e.g., [60, 120, 180].

    Returns:
    - Cleaned and whitened GWpy TimeSeries.
    """

    if notches is None:
        notches = [60 * i for i in range(1, 5)]

    # Bandpass
    strain_bp = strain.bandpass(low, high)
    for freq in notches:
        strain_bp = strain_bp.notch(freq)

    # Estimate PSD from full bandpassed strain
    psd = strain_bp.psd(fftlength=fftlength)

    # Crop AFTER filtering and psd
    strain_zoom = strain_bp.crop(gps_event - crop_width, gps_event + crop_width)

    # Whiten using precomputed PSD
    strain_white = strain_zoom.whiten(asd=np.sqrt(psd))

    return strain_white


# ───────── USER PARAMS ───────── #
gps_event = 1126259462          # GW150914
detector = "H1"                 # use "L1", "V1", etc. for others
half_window = 128               # total segment = 2 × this
crop_width = 2                  # seconds plotted around the event
# ─────────────────────────────── #

# 1. Fetch & validate strain data
strain = download(detector, gps_event, window=half_window)
# After zooming the strain:
strain_zoom = strain.crop(gps_event - crop_width, gps_event + crop_width)

# Preprocess the strain data
strain_clean = preprocess(strain_zoom)

# Plot the cleaned signal
plot = strain_clean.plot()
ax = plot.gca()
ax.set_title(f"{detector} strain – GW150914 (preprocessed)")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Strain (whitened, filtered)")

plt.show()
