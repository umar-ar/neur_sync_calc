# README

## Overview
This script is designed for processing and analyzing spike train data from intracortical microstimulation (ICMS) experiments. It extracts spike train data from pickle files, calculates synchronization profiles using PySpike, and generates visualizations of synchronization patterns across stimulation events. The main features include:
- Extraction of spike trains relative to stimulation events.
- Calculation of synchronization profiles using SPIKE-synchronization metrics.
- Visualization of average synchronization profiles and adaptive time window distributions.
- Processing and analysis of multiple experimental sessions.

## Prerequisites
Before running this script, ensure you have the following Python packages installed:
- `pickle`: For reading the data files.
- `numpy`: For numerical operations.
- `pyspike`: For synchronization analysis of spike trains.
- `matplotlib`: For plotting graphs.
- `os` and `datetime`: For file handling and timestamp formatting.

Install these packages using the following command:
pip install numpy pyspike matplotlib


## Usage Instructions

### 1. Data Requirements
- The data should be in pickle file format, containing at least the following keys:
  - `unit_spike_train_dict`: A dictionary with unit IDs as keys and spike times as values.
  - `stim_trains`: A list of stimulation timestamps.
  - `sampling_rate`: The sampling rate of the recording.

### 2. Extracting Spike Trains
The function `extract_spike_trains_from_pickle()` extracts spike trains relative to each stimulation event within specified time windows.

**Parameters:**
- `file_path`: Path to the pickle file.
- `pre_stimulus_time`: Time (in seconds) before the stimulus to start the spike train window (default: `-1.2s`).
- `post_stimulus_time`: Time (in seconds) after the stimulus to end the spike train window (default: `1.9s`).
- `extract_entire_session`: If `True`, extracts spikes for the whole session; otherwise, only around each stimulation event.

### 3. Calculating Synchronization Profiles
The function `calculate_sync_profiles()` computes the synchronization profile for each stimulation event using the SPIKE-synchronization metric.

### 4. Plotting Synchronization Profiles
The function `plot_average_sync_profile()` visualizes the average synchronization profile across all stimulation events, highlighting key time points.

### 5. Processing Multiple Sessions
The function `process_multiple_sessions_from_directory()` automates the extraction and analysis of multiple session files in a directory. It calculates and plots synchronization profiles for each session and also displays the overall synchronization level for each session.

**Parameters:**
- `directory_path`: Path to the directory containing pickle files.
- The script assumes that session dates are formatted as `ICMS92_DD-MMM-YYYY` in the filenames.

### Example Usage
To process all sessions in the `spike_trains` directory, use the following:
directory_path = 'spike_trains' process_multiple_sessions_from_directory(directory_path)


This command will automatically extract data from each session, compute synchronization profiles, and generate plots for visualization.

## Output
- **Synchronization Profiles:** Line plots of average synchronization levels around stimulation events.
- **Adaptive Time Window Distribution:** Histogram of time window sizes used during synchronization analysis.
- **Session Comparison:** Bar chart showing the average synchronization value for each session.

## Important Notes
- **Data Format:** The pickle file must be structured as described for correct processing.
- **Adaptive Time Windows:** The histogram of adaptive time windows focuses on smaller values to highlight synchronization dynamics.

## Troubleshooting
- **Data Loading Errors:** Ensure that the file path and data structure match the expected format.
- **Unexpected Plot Results:** Verify that spike trains and stimulation timestamps are correctly aligned.

## License
This script is open for academic and non-commercial use. If you use it in your research, please cite appropriately.
