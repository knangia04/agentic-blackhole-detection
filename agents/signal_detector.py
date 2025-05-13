from pycbc.types import TimeSeries as PyCBCTimeSeries
from matched_filter import run_matched_filter


def detect_signal(snr, t0, snr_threshold=8.0):
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
    relative_peak_time = snr.sample_times[peak]

    # Convert both to floats in seconds
    t0_sec = t0.to_value("s") if hasattr(t0, "to_value") else float(t0)
    t_rel_sec = relative_peak_time.to_value("s") if hasattr(relative_peak_time, "to_value") else float(relative_peak_time)

    gps_peak_time = relative_peak_time 


    detection = peak_snr > snr_threshold
    # print(f"[Detection] Peak SNR = {peak_snr:.2f} at GPS time = {gps_peak_time:.4f} → {'✅' if detection else '❌'}")
    return detection, peak_snr, float(gps_peak_time)
