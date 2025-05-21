def run_matched_filter(strain, sample_rate, mass1, mass2, distance, gps_event=None, search_window=0.5):
    from pycbc.waveform import get_td_waveform
    from pycbc.filter import matched_filter
    from pycbc.psd import interpolate, inverse_spectrum_truncation
    import matplotlib.pyplot as plt
    import numpy as np

    # 1. Generate template waveform
    hp, _ = get_td_waveform(
        approximant="SEOBNRv4",
        mass1=mass1,
        mass2=mass2,
        delta_t=1.0 / sample_rate,
        f_lower=30,
        distance=distance
    )
    # Crop template only if long enough
    # crop_margin = min(0.1, hp.duration / 5)
    hp = hp.crop(0.075, 0.075)

    # hp = hp.crop(0.2, 0.2)

    # 2. Estimate PSD
    psd = strain.psd(4)
    psd = interpolate(psd, strain.delta_f)
    psd = inverse_spectrum_truncation(psd, int(4 * sample_rate), low_frequency_cutoff=30)

    # 3. Run matched filter
    hp.resize(len(strain))  # ensure same length
    snr = matched_filter(hp, strain, psd=psd, low_frequency_cutoff=30)


    # 4. Optional: focus on ±search_window around gps_event
    if gps_event:
        t0 = strain.start_time

        start = gps_event - search_window
        end = gps_event + search_window

        available_start = snr.start_time 
        available_end = snr.end_time

        safe_start = max(available_start, start)
        safe_end = min(available_end, end)

        if safe_end <= safe_start:
            raise ValueError(f"SNR window is invalid: [{safe_start}, {safe_end}] not in [{available_start}, {available_end}]")

        # print(f"[SNR Crop] GPS window: [{safe_start}, {safe_end}]")
        # print(f"[SNR Actual Bounds] {snr.start_time} → {snr.end_time}")
        # print(f"[Requested Crop] {safe_start} → {safe_end}")

        if safe_end > snr.end_time or safe_start < snr.start_time:
            raise ValueError(f"SNR crop range [{safe_start}, {safe_end}] is outside valid range [{snr.start_time}, {snr.end_time}]")

        snr = snr.time_slice(safe_start, safe_end)

    # 5. Peak detection — search near expected GPS time
    if gps_event:
        expected_idx = np.abs(snr.sample_times.numpy() - gps_event).argmin()
        window_size = int(0.05 * snr.sample_rate)  # 50 ms in samples

        start = max(0, expected_idx - window_size)
        end = min(len(snr), expected_idx + window_size)

        local_window = abs(snr)[start:end]
        local_peak = local_window.numpy().argmax() + start  # ✅ FIXED
        peak = local_peak
    else:
        peak = abs(snr).numpy().argmax()

    peak_snr = abs(snr[peak])
    peak_time = snr.sample_times[peak]

    # print(f"Peak SNR: {peak_snr:.2f} at time {peak_time:.2f} s")

    # 6. Plot SNR with peak and expected time
    plt.plot(snr.sample_times, abs(snr))
    plt.title("Matched Filter SNR Time Series")
    plt.axvline(peak_time, color="r", linestyle="--", label="Peak")
    if gps_event:
        plt.axvline(gps_event, color="g", linestyle=":", label="Expected Event")
    plt.xlabel("Time (s)")
    plt.ylabel("SNR")
    plt.grid()
    plt.legend()
    # plt.show()

    return snr

