# visualize.py
"""
Quick–look plot of the GW150914 signal.

This module provides various visualization functions for gravitational wave data:
1. Raw data visualization
2. Preprocessed data visualization 
3. Matched filtering results visualization
4. Combined analysis pipeline

Edit the USER PARAMS block to change GPS time, detector, or crop width.
"""

from matplotlib import pyplot as plt
from agents.fetch_validate import download
from matched_filter import run_matched_filter
from preprocess import preprocess
from gwpy.timeseries import TimeSeries as GWpyTimeSeries
from pycbc.types import TimeSeries as PyCBCTimeSeries


# ───────── USER PARAMS ───────── #
gps_event = 1126259462          # GW150914
detector = "H1"                 # use "L1", "V1", etc. for others
half_window = 256               # total segment = 2 × this
crop_width = 2                 # seconds plotted around the event
# ─────────────────────────────── #


def fetch_data(detector, gps_time, window):
    """
    Fetch gravitational wave strain data.
    
    Parameters:
    - detector: Detector name (e.g., "H1", "L1", "V1")
    - gps_time: GPS time of the event
    - window: Half-width of segment in seconds
    
    Returns:
    - GWpy TimeSeries object containing strain data
    """
    return download(detector, gps_time, window=window)


def crop_data(strain, center_time, width):
    """
    Crop strain data to a specific time window.
    
    Parameters:
    - strain: GWpy TimeSeries object
    - center_time: Center time (GPS)
    - width: Half-width of segment in seconds
    
    Returns:
    - Cropped GWpy TimeSeries
    """
    return strain.crop(center_time - width, center_time + width)


def plot_raw_strain(strain, detector_name, event_name="GW150914", save_path=None):
    """
    Plot raw strain data.
    
    Parameters:
    - strain: GWpy TimeSeries of strain data
    - detector_name: Name of the detector for title
    - event_name: Name of the event for title
    - save_path: Path to save figure (if None, display instead)
    """
    plot = strain.plot()
    ax = plot.gca()
    ax.set_title(f"{detector_name} strain – {event_name}")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Strain")
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def plot_processed_strain(strain, detector_name, event_name="GW150914", save_path=None):
    """
    Plot preprocessed strain data.
    
    Parameters:
    - strain: GWpy TimeSeries of processed strain data
    - detector_name: Name of the detector for title
    - event_name: Name of the event for title
    - save_path: Path to save figure (if None, display instead)
    """
    plot = strain.plot()
    ax = plot.gca()
    ax.set_title(f"{detector_name} strain – {event_name} (preprocessed)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Strain (whitened, filtered)")
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def convert_gwpy_to_pycbc(gwpy_timeseries):
    """
    Convert GWpy TimeSeries to PyCBC TimeSeries.
    
    Parameters:
    - gwpy_timeseries: GWpy TimeSeries object
    
    Returns:
    - PyCBC TimeSeries object
    """
    return PyCBCTimeSeries(
        gwpy_timeseries.value, 
        delta_t=1.0 / gwpy_timeseries.sample_rate.value
    )


def perform_raw_analysis(strain, gps_time, crop_width, detector_name):
    """
    Perform and visualize analysis on raw strain data.
    
    Parameters:
    - strain: Full GWpy TimeSeries
    - gps_time: Event time in GPS seconds
    - crop_width: Width to crop around event in seconds
    - detector_name: Name of the detector
    """
    # Crop raw data
    strain_zoom = crop_data(strain, gps_time, crop_width)
    
    # Plot raw data
    plot_raw_strain(strain_zoom, detector_name)


def perform_processed_analysis(strain, gps_time, crop_width, detector_name):
    """
    Perform and visualize analysis on processed strain data.
    
    Parameters:
    - strain: Full GWpy TimeSeries
    - gps_time: Event time in GPS seconds
    - crop_width: Width to crop around event in seconds
    - detector_name: Name of the detector
    """
    # Preprocess returns already cropped, whitened signal
    strain_clean = preprocess(strain, gps_event=gps_time, crop_width=crop_width)

    # Plot preprocessed signal
    plot_processed_strain(strain_clean, detector_name)

    # Convert for PyCBC
    strain_pycbc = convert_gwpy_to_pycbc(strain_clean)

    # Run matched filtering
    run_matched_filter(strain_pycbc, strain_clean.sample_rate.value)


def main():
    """Main function to run the visualization pipeline."""
    # Fetch data
    strain = fetch_data(detector, gps_event, half_window)
    
    # Perform raw data analysis
    perform_raw_analysis(strain, gps_event, crop_width, detector)
    
    # Perform processed data analysis
    perform_processed_analysis(strain, gps_event, crop_width, detector)
    
    from agents.parameter_estimator import estimate_parameters

    estimate_parameters(strain, gps=gps_event)



if __name__ == "__main__":
    main()