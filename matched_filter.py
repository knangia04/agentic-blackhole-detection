from pycbc.waveform import get_td_waveform
from pycbc.filter import matched_filter
from pycbc.psd import interpolate, inverse_spectrum_truncation
from pycbc.types import TimeSeries
import matplotlib.pyplot as plt

def run_matched_filter(strain, sample_rate):
    # 1. Generate template waveform (GW150914-like)
    hp, _ = get_td_waveform(approximant="SEOBNRv4",  # accurate BBH model
                           mass1=36,
                           mass2=29,
                           delta_t=1.0 / sample_rate,
                           f_lower=30)

    # Resize template to match strain length
    template_length = len(strain)
    hp.resize(template_length)

    # 2. Estimate PSD from the strain
    psd = strain.psd(4)  # 4-second FFTs
    psd = interpolate(psd, strain.delta_f)
    psd = inverse_spectrum_truncation(psd, int(4 * sample_rate), low_frequency_cutoff=30)

    # 3. Run matched filter
    snr = matched_filter(hp, strain, psd=psd, low_frequency_cutoff=30)

    # 4. Trim edges and find peak
    try:
        snr = snr.crop(4, 4)  # Try to crop 4 seconds from each end
    except ValueError:
        # If we don't have enough data, crop less
        crop_time = min(4, len(snr) / snr.sample_rate / 4)
        snr = snr.crop(crop_time, crop_time)

    peak = abs(snr).numpy().argmax()
    snr_peak = abs(snr[peak])
    peak_time = snr.sample_times[peak]

    print(f"Peak SNR: {snr_peak:.2f} at time {peak_time:.2f} s")

    # 5. Plot SNR
    plt.plot(snr.sample_times, abs(snr))
    plt.title("Matched Filter SNR Time Series")
    plt.xlabel("Time (s)")
    plt.ylabel("SNR")
    plt.grid()
    plt.show()

    return snr


# from pycbc.types import TimeSeries
# strain_pyc = TimeSeries(strain_clean.value, delta_t=1.0/strain_clean.sample_rate.value)

# # Run matched filtering
# run_matched_filter(strain_pyc, strain_clean.sample_rate.value)