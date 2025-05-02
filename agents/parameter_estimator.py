import bilby
from gwpy.timeseries import TimeSeries
from bilby.gw.detector import InterferometerList
from bilby.gw.source import lal_binary_black_hole

def estimate_parameters(
    strain: TimeSeries,
    gps: int,
    duration: int = 4,
    f_low: float = 20,
    label: str = "GW150914_estimation",
    outdir: str = "bilby_output",
):
    # Prepare strain segment around merger
    strain_segment = strain.crop(gps - duration // 2, gps + duration // 2)

    # Convert to Bilby Interferometer
    interferometer = bilby.gw.detector.Interferometer("H1")
    interferometer.strain_data.set_from_gwpy_timeseries(strain_segment)
    interferometer.minimum_frequency = f_low

    interferometers = InterferometerList(["H1"])
    interferometers[0] = interferometer

    # Define prior dictionary
    priors = bilby.gw.prior.BBHPriorDict()
    priors["mass_1"] = bilby.core.prior.Uniform(20, 80, "mass_1")
    priors["mass_2"] = bilby.core.prior.Uniform(20, 80, "mass_2")
    priors["luminosity_distance"] = bilby.core.prior.Uniform(100, 1000, "luminosity_distance")
    priors["theta_jn"] = bilby.core.prior.Uniform(0, 3.14, "theta_jn")
    priors["phase"] = bilby.core.prior.Uniform(0, 2 * 3.1415, "phase")
    priors["geocent_time"] = bilby.core.prior.Uniform(gps - 0.1, gps + 0.1, "geocent_time")

    # Define waveform generator
    waveform_generator = bilby.gw.waveform_generator.WaveformGenerator(
        duration=duration,
        sampling_frequency=strain.sample_rate.value,
        frequency_domain_source_model=lal_binary_black_hole,
        parameters=None,
    )

    # Likelihood
    likelihood = bilby.gw.likelihood.GravitationalWaveTransient(
        interferometers=interferometers,
        waveform_generator=waveform_generator,
        priors=priors,
    )

    # Run sampler
    result = bilby.run_sampler(
        likelihood=likelihood,
        priors=priors,
        sampler="dynesty",
        label=label,
        outdir=outdir,
        nlive=500,
    )

    result.plot_corner()
    return result
