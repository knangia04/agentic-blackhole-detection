from pycbc.types import TimeSeries as PyCBCTimeSeries
from matched_filter import run_matched_filter


def detect_signal(snr, snr_threshold=8.0):
    """
    Run matched filter detection on preprocessed strain data.

    Parameters:
    - strain_gwpy: GWpy TimeSeries (whitened, filtered, cropped)
    - snr_threshold: SNR threshold to declare detection

    Returns:
    - detection: bool
    - peak_snr: float
    - peak_time: float
    """
    peak = abs(snr).numpy().argmax()
    peak_snr = abs(snr[peak])
    peak_time = snr.sample_times[peak]

    detection = peak_snr > snr_threshold
    print(f"[Detection] Peak SNR = {peak_snr:.2f} at t = {peak_time:.2f} sec → {'✅ DETECTED' if detection else '❌ NO DETECTION'}")
    return detection, peak_snr, peak_time
