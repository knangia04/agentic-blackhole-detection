"""
Preprocessing module for gravitational wave strain data.

Steps:
1. Bandpass filter the signal (default: 30–500 Hz)
2. Apply notch filters (e.g., 60 Hz power line)
3. Estimate PSD over the full window
4. Crop to ±crop_width around the event
5. Whiten the cropped strain using full PSD
"""

from gwpy.timeseries import TimeSeries
import numpy as np


def preprocess(
    strain: TimeSeries,
    gps_event: float,
    crop_width: float = 2.0,
    f_low: float = 30.0,
    f_high: float = 500.0,
    fftlength: float = 4.0,
    notches=None
) -> TimeSeries:
    if notches is None:
        notches = [60 * i for i in range(1, 5)]

    # 1. Bandpass filter full strain segment
    strain_filtered = strain.bandpass(f_low, f_high)
    for freq in notches:
        strain_filtered = strain_filtered.notch(freq)

    # 2. Estimate PSD on full segment
    psd = strain_filtered.psd(fftlength=fftlength)

    # 3. Crop to region around event
    strain_zoom = strain_filtered.crop(gps_event - crop_width, gps_event + crop_width)

    # 4. Whiten cropped strain using full-segment PSD
    strain_white = strain_zoom.whiten(asd=np.sqrt(psd))

    return strain_white
