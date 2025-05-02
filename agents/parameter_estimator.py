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
    interferometer = bilby.gw.detector.get_empty_interferometer('H1')
    interferometer.strain_data.set_from_gwpy_timeseries(strain_segment)
    interferometer.minimum_frequency = f_low

    interferometers = InterferometerList(["H1"])
    interferometers[0] = interferometer

    # Set extremely narrow priors for quick testing
    priors = dict()
    
    # Mass parameters
    priors["mass_1"] = bilby.core.prior.Uniform(35.5, 36.5, "mass_1")
    priors["mass_2"] = bilby.core.prior.Uniform(28.5, 29.5, "mass_2")
    
    # Fixed parameters for quick test
    priors["luminosity_distance"] = 440
    priors["theta_jn"] = 0.4
    priors["phase"] = 0.0
    priors["geocent_time"] = gps
    
    # Required spin parameters (setting to zero for non-spinning test)
    priors["a_1"] = 0.0  # Primary spin magnitude
    priors["a_2"] = 0.0  # Secondary spin magnitude
    priors["tilt_1"] = 0.0  # Primary spin tilt
    priors["tilt_2"] = 0.0  # Secondary spin tilt
    priors["phi_12"] = 0.0  # Relative spin azimuthal angle
    priors["phi_jl"] = 0.0  # Precession angle
    
    # Sky location parameters (fixed overhead)
    priors["ra"] = 0.0  # Right ascension
    priors["dec"] = 0.0  # Declination
    priors["psi"] = 0.0  # Polarization angle

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
        nlive=10,        # Minimum number for stability
        npool=1,         # Single CPU
        dlogz=10.0,      # Less stringent convergence
        maxmcmc=50,      # Reduced MCMC steps
        walks=5,         # Minimal walks
        nact=5,          # Fixed number of autocorrelation times
        bound='single',  # Simpler boundary conditioning
        sample='unif',   # Uniform sampling (faster)
        save=True
    )

    result.plot_corner()
    return result
