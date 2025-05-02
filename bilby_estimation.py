import bilby
import numpy as np
from bilby.gw.detector import InterferometerList

# Setup basic parameters
duration = 4
sampling_frequency = 2048
outdir = "bilby_out"
label = "GW150914"

bilby.core.utils.setup_logger()

# Define prior ranges
priors = bilby.gw.prior.BBHPriorDict()
priors['mass_1'] = bilby.core.prior.Uniform(30, 50, 'mass_1')
priors['mass_2'] = bilby.core.prior.Uniform(20, 40, 'mass_2')
priors['luminosity_distance'] = bilby.core.prior.Uniform(100, 1000, 'luminosity_distance')
priors['geocent_time'] = bilby.core.prior.Uniform(1126259462.3, 1126259462.5, 'geocent_time')
priors['theta_jn'] = bilby.core.prior.Uniform(0, np.pi, 'theta_jn')
priors['psi'] = bilby.core.prior.Uniform(0, np.pi, 'psi')

# Load GW150914 data
ifos = InterferometerList(['H1', 'L1'])
ifos.set_strain_data_from_gracedb("GW150914", duration=duration, sampling_frequency=sampling_frequency)

# Create waveform generator
waveform_generator = bilby.gw.waveform_generator.WaveformGenerator(
    duration=duration,
    sampling_frequency=sampling_frequency,
    frequency_domain_source_model=bilby.gw.source.lal_binary_black_hole
)

# Likelihood
likelihood = bilby.gw.likelihood.GravitationalWaveTransient(
    interferometers=ifos, waveform_generator=waveform_generator
)

# Run sampler
result = bilby.run_sampler(
    likelihood=likelihood,
    priors=priors,
    sampler='dynesty',
    nlive=500,
    outdir=outdir,
    label=label
)

# Plot corner
result.plot_corner()
