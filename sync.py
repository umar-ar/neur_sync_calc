import pickle
import numpy as np
import pyspike as spk
import matplotlib.pyplot as plt
import os
from datetime import datetime

def extract_spike_trains_from_pickle(file_path, pre_stimulus_time=-1.2, plot_start_time=-0.7, post_stimulus_time=1.9, extract_entire_session=False):
    # Load the pickle file
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    
    # Extract relevant data
    unit_spike_train_dict = data['unit_spike_train_dict']
    stim_trains = data['stim_trains']
    sampling_rate = data['sampling_rate']

    # Convert times to samples
    pre_stimulus_samples = int(pre_stimulus_time * sampling_rate)
    post_stimulus_samples = int(post_stimulus_time * sampling_rate)
    
    # Initialize dictionary to store spike train objects for each stimulation event
    stim_event_spike_trains = []
    
    # Iterate over each stimulation event
    for stim_index, stim_timestamps in enumerate(stim_trains):
        # Ensure stim_timestamps is a list of single stimulation events
        if not isinstance(stim_timestamps, list):
            stim_timestamps = [stim_timestamps]
        
        # Only consider the first timestamp for each stimulation train to avoid redundancy
        if stim_timestamps:
            stim_time = stim_timestamps[0]
            # Define time window for the spike train extraction
            start_time = stim_time + pre_stimulus_samples
            end_time = stim_time + post_stimulus_samples

            # Create spike trains for each unit in the given time window
            spike_trains = {}
            for unit_id, spike_times in unit_spike_train_dict.items():
                # Extract spikes within the time window
                spikes_in_window = spike_times[(spike_times >= start_time) & (spike_times <= end_time)]
                # Adjust spike times to be relative to the stimulus time (e.g., -1.2s to 1.9s)
                adjusted_spike_times = (spikes_in_window - stim_time) / sampling_rate
                # Create a PySpike SpikeTrain object
                spike_train = spk.SpikeTrain(adjusted_spike_times, edges=(pre_stimulus_time, post_stimulus_time))
                spike_trains[unit_id] = spike_train
            
            # Store the spike trains for the current stimulation event
            stim_event_spike_trains.append({
                'stim_index': stim_index,
                'stim_time': stim_time,
                'spike_trains': spike_trains
            })

    # Print the number of stimulation events
    print(f"Total number of stimulation events: {len(stim_trains)}")

    # Print discrepancy if the number of extracted spike trains is different from the total number of stimulation events
    if len(stim_event_spike_trains) != len(stim_trains):
        print(f"Warning: Extracted spike trains for {len(stim_event_spike_trains)} stimulation events, expected {len(stim_trains)}.")

    return stim_event_spike_trains

def calculate_sync_profiles(stim_event_spike_trains):
    sync_profiles = []
    min_length = float('inf')
    adaptive_time_windows = []
    
    # Calculate sync profile for each stimulation event
    for event in stim_event_spike_trains:
        spike_trains = list(event['spike_trains'].values())
        if len(spike_trains) > 1:
            # Calculate the SPIKE-Synchronization profile using PySpike
            sync_profile = spk.spike_sync_profile(spike_trains)
            # Normalize sync profile to be between 0 and 1
            sync_profile.y = sync_profile.y / len(spike_trains)
            sync_profiles.append(sync_profile.y)
            min_length = min(min_length, len(sync_profile.y))
            # Store adaptive time windows used by PySpike
            adaptive_time_windows.extend(sync_profile.x[1:] - sync_profile.x[:-1])
    
    # Truncate all sync profiles to the minimum length to allow averaging
    truncated_sync_profiles = [profile[:min_length] for profile in sync_profiles]
    
    # Calculate average sync profile across all stimulation events
    if truncated_sync_profiles:
        avg_sync_profile = np.mean(truncated_sync_profiles, axis=0)
        avg_sync_value = np.mean(avg_sync_profile)
    else:
        avg_sync_profile = []
        avg_sync_value = 0
    
    return avg_sync_profile, avg_sync_value, adaptive_time_windows

def plot_average_sync_profile(avg_sync_profile, adaptive_time_windows, pre_stimulus_time=-1.2, plot_start_time=-0.7, post_stimulus_time=1.4, full_post_stimulus_time=1.9, session_name='Session'):
    # Create time axis for plotting
    time_axis = np.linspace(pre_stimulus_time, full_post_stimulus_time, len(avg_sync_profile))
    
    # Select the portion of the profile to plot starting from plot_start_time to post_stimulus_time
    plot_indices = np.where((time_axis >= plot_start_time) & (time_axis <= post_stimulus_time))[0]
    time_axis_plot = time_axis[plot_indices]
    avg_sync_profile_plot = avg_sync_profile[plot_indices]
    
    # Plot the average sync profile
    plt.figure(figsize=(10, 5))
    plt.plot(time_axis_plot, avg_sync_profile_plot, label='Average Sync Profile', color='b')
    plt.xlabel('Time (s)')
    plt.ylabel('Synchronization')
    plt.title(f'Average Synchronization Profile Across Stimulation Events ({session_name})')
    plt.axvline(x=0, color='r', linestyle='--', label='Stimulation Onset')
    plt.axvline(x=0.7, color='g', linestyle='--', label='Stimulation End')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Plot the adaptive time window distribution as a histogram with a limited x-axis range
    plt.figure(figsize=(10, 5))
    plt.hist(adaptive_time_windows, bins=50, color='m', alpha=0.7)
    plt.xlabel('Adaptive Time Window (s)')
    plt.ylabel('Frequency')
    plt.title(f'Adaptive Time Window Distribution ({session_name})')
    plt.xlim(0, 0.08)  # Limit the x-axis range to focus on smaller time window values
    plt.grid(True)
    plt.show()

def calculate_session_sync_profile(stim_event_spike_trains):
    spike_trains = []
    for event in stim_event_spike_trains:
        spike_trains.extend(list(event['spike_trains'].values()))
    if len(spike_trains) > 1:
        # Calculate the SPIKE-Synchronization value for the entire session
        avg_sync_value = spk.spike_sync(spike_trains)
    else:
        avg_sync_value = 0  # If only one spike train, sync is not defined
    
    return avg_sync_value

def process_multiple_sessions_from_directory(directory_path, pre_stimulus_time=-1.2, plot_start_time=-0.7, post_stimulus_time=1.4, full_post_stimulus_time=1.9):
    # Get all pickle files in the directory
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.pkl')]
    
    # Sort file paths by their session dates (assuming session date is in the filename in 'ICMS92_DD-MMM-YYYY' format)
    file_paths.sort(key=lambda x: datetime.strptime(os.path.basename(x).split('_')[1].replace('.pkl', ''), '%d-%b-%Y'))
    
    avg_sync_values = []
    session_names = []

    for file_path in file_paths:
        # Extract the session name from the file path
        session_name = os.path.basename(file_path).split('.')[0]
        
        # Extract spike trains for the entire session
        session_spike_trains = extract_spike_trains_from_pickle(file_path, pre_stimulus_time, full_post_stimulus_time, extract_entire_session=True)
        
        # Calculate synchronization profiles around stimulation events
        avg_sync_profile, avg_sync_value, adaptive_time_windows = calculate_sync_profiles(session_spike_trains)
        
        # Store average synchronization value for plotting later (entire session)
        avg_sync_value_session = calculate_session_sync_profile(session_spike_trains)
        avg_sync_values.append(avg_sync_value_session)
        session_names.append(session_name)
        
        # Plot average sync profile for the session around stimulation events
        plot_average_sync_profile(avg_sync_profile, adaptive_time_windows, pre_stimulus_time, plot_start_time, post_stimulus_time, full_post_stimulus_time, session_name)
    
    # Plot average synchronization value for each session (entire session)
    plt.figure(figsize=(10, 5))
    plt.bar(session_names, avg_sync_values, color='b')
    plt.xlabel('Session')
    plt.ylabel('Average Synchronization for Entire Session')
    plt.title('Average Synchronization Across Entire Sessions')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y')
    plt.show()

# Example usage
directory_path = 'spike_trains'
process_multiple_sessions_from_directory(directory_path)