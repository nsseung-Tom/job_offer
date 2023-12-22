import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def process_outliers(file_path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Create wage_difference column 
    df['wage_difference'] = np.log(df['offered_wage'] / df['previous_wage'])

    # Calculate the IQR (Interquartile Range)
    Q1 = df['wage_difference'].quantile(0.25)
    Q3 = df['wage_difference'].quantile(0.75)
    IQR = Q3 - Q1

    # Define the lower and upper bounds to identify outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR    

    # Exclude outliers from the DataFrame
    filtered_df = df[(df['wage_difference'] >= lower_bound) & (df['wage_difference'] <= upper_bound)]

    # Display the length of filtered DataFrame
    print("Length of data excluding outliers:", len(filtered_df))  # Print the length of final_data
    
    return filtered_df

def group_data(filtered_df, interval_size):
    num_intervals = round(2 / interval_size)
    bins = [-1 + i * interval_size for i in range(num_intervals + 1)]

    filtered_df['wage_diff_interval'] = pd.cut(filtered_df['wage_difference'], bins=bins, right=False)

    grouped_data = filtered_df.groupby('wage_diff_interval')['acceptance_yn'].agg(
        total_count='count', accept_count=lambda x: (x == 'y').sum()
    ).reset_index()
    grouped_data['acceptance_ratio_per_interval'] = grouped_data['accept_count'] / grouped_data['total_count']

    return grouped_data

def save_line_graph(grouped_data, filename_prefix, result_folder):
    plt.figure(figsize=(12, 8))  # Larger figure size

    # Plotting the line graph with larger dimensions
    x_values = grouped_data['wage_diff_interval'].astype(str)
    y_values = grouped_data['acceptance_ratio_per_interval'].values
    plt.plot(x_values, y_values, marker='o', linestyle='-', color='skyblue', markersize=8)
    plt.xlabel('Wage Difference Intervals')
    plt.ylabel('Acceptance Ratio')
    plt.title(f'Acceptance Ratio within Wage Difference Intervals\nFile: {filename_prefix}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot as an image file
    plot_filename = os.path.join(result_folder, f"{filename_prefix}_graph.jpg")
    plt.savefig(plot_filename, bbox_inches='tight', pad_inches=0.5)
    plt.close()  # Close the plot to avoid display in the notebook
    print(f"Saved line graph for {filename_prefix}")
    
def interval_array_to_string(interval_array):
    # Convert IntervalArray to string representation
    interval_str = interval_array.astype(str)
    return interval_str

def save_table_csv(grouped_data, filename_prefix, result_folder):
    # Convert IntervalArray columns to strings
    grouped_data_str = grouped_data.apply(lambda col: interval_array_to_string(col) if col.dtype.name == 'IntervalArray' else col)
    # Generate the output filename for CSV
    csv_filename = os.path.join(result_folder, f"{filename_prefix}_grouped_data.csv")
    # Save grouped_data as a CSV file
    grouped_data_str.to_csv(csv_filename, index=False)
    print(f"Saved grouped data as CSV file for {filename_prefix}")

# List of file paths
file_paths = [
    'data/preprocessed_job2_wage_per_hr_only.csv', 
    'data/preprocessed_job2_wage_convert_to_hr.csv',
    'data/preprocessed_prev_cps_wage_per_hr_only.csv',
    'data/preprocessed_prev_cps_wage_convert_to_hr.csv'
]

# Folder name for saving results
result_folder = 'result'

# Check if the 'result' folder exists, if not, create it
if not os.path.exists(result_folder):
    os.makedirs(result_folder)

# Iterate through file paths
for file_path in file_paths:
    # Load the DataFrame and process outliers
    df = process_outliers(file_path) 
    interval_size = 0.25  # Set your interval size here
    # Group the data
    grouped_data = group_data(df, interval_size)

    # Extract filename without extension
    filename_prefix = os.path.splitext(os.path.basename(file_path))[0]
    
    # Save line graph and table CSV in the 'result' folder
    save_line_graph(grouped_data, filename_prefix, result_folder)
    save_table_csv(grouped_data, filename_prefix, result_folder)
