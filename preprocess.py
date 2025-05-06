from gwpy.timeseries import TimeSeries
import numpy as np


def preprocess(
    strain: TimeSeries,
    gps_event: float,
    crop_width: float = 2,
    f_low: float = 30,
    f_high: float = 500,
    fftlength: float = 4,
    notches=None
) -> TimeSeries:
    if notches is None:
        notches = [60 * i for i in range(1, 5)]

    # 1. Bandpass the full strain
    strain_filtered = strain.bandpass(f_low, f_high)
    for freq in notches:
        strain_filtered = strain_filtered.notch(freq)

    # 2. Estimate PSD from the full bandpassed signal
    psd = strain_filtered.psd(fftlength=fftlength)

    # 3. Crop a tight window around the event AFTER PSD estimation
    cropped = strain_filtered.crop(gps_event - crop_width, gps_event + crop_width)

    # 4. Whiten the cropped window using full-interval PSD
    whitened = cropped.whiten(asd=np.sqrt(psd))

    return whitened
