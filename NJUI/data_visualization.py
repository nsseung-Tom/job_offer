import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import statsmodels.api as sm

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
    
# Generate quantile bins
def group_data_quantile_bins(filtered_df, exclude_option):
    wage_0 = filtered_df[filtered_df['wage_difference']==0]
    wage_1 = filtered_df[filtered_df['wage_difference']!=0]
    
    # Drop duplicate edges
    if exclude_option == 1 : # exclude don't know
        bins = [-0.92, -0.536, -0.36, -0.237, -0.142, 0.0, 0.133, 0.262, 0.7]
    elif exclude_option == 2 : # include don't know 
        bins = [-0.92, -0.549, -0.366, -0.248, -0.154, 0.0, 0.134, 0.287, 0.7]
    
    # Wage != 0일때 먼저 grouped 
    # Bin the wage_difference column using the quantile bins
    wage_1['wage_diff_quantile_bin'] = pd.cut(wage_1['wage_difference'], bins=bins, include_lowest=True)

    # Calculate average offer within each quantile bin
    grouped_data_not_zero = wage_1.groupby('wage_diff_quantile_bin').agg(
        avg_offer=('wage_difference', 'mean'),
        total_count=('acceptance_yn', 'count'),
        accept_count=('acceptance_yn', lambda x: (x == 'y').sum())
    ).reset_index()

    grouped_data_not_zero['acceptance_ratio_per_interval'] = grouped_data_not_zero['accept_count'] / grouped_data_not_zero['total_count']
    
    
    # Wage == 0 일때 
    grouped_data0 = wage_0.groupby('wage_difference').agg(
        avg_offer=('wage_difference', 'mean'),
        total_count=('acceptance_yn', 'count'),
        accept_count=('acceptance_yn', lambda x: (x == 'y').sum())
    ).reset_index()

    grouped_data0['acceptance_ratio_per_interval'] = grouped_data0['accept_count'] / grouped_data0['total_count']
    grouped_data0['wage_diff_quantile_bin'] = '[0.0, 0.0]'
    grouped_zero = grouped_data0.loc[:,['wage_diff_quantile_bin', 'avg_offer', 'total_count', 'accept_count', 'acceptance_ratio_per_interval'
]]
    return grouped_data_not_zero, grouped_zero

# Graph for quantile bins only 
def generate_and_save_final_graph(filtered_df, exclude_option):
    filtered_df['accept_yn'] = np.where(filtered_df['acceptance_yn'] == 'y', 1, 0)
    positive_intervals = filtered_df[filtered_df['wage_difference'] > 0]
    negative_intervals = filtered_df[filtered_df['wage_difference'] < 0]

    grouped_not_zero, grouped_zero = group_data_quantile_bins(filtered_df, exclude_option)

    positive_model = sm.OLS(positive_intervals['accept_yn'], sm.add_constant(positive_intervals['wage_difference'])).fit()
    negative_model = sm.OLS(negative_intervals['accept_yn'], sm.add_constant(negative_intervals['wage_difference'])).fit()

    plt.figure(figsize=(15, 10))

    sns.regplot(
        x=positive_intervals['wage_difference'],
        y=positive_intervals['accept_yn'],
        scatter=False,
        color='blue'
    )

    sns.regplot(
        x=negative_intervals['wage_difference'],
        y=negative_intervals['accept_yn'],
        scatter=False,
        color='red'
    )

    plt.axvline(x=0, color='black', linestyle='--', label='wage_diff = 0')

    x_value = grouped_zero['avg_offer']
    y_value = grouped_zero['acceptance_ratio_per_interval']
    plt.scatter(x_value, y_value, color='orange', label='Specific Value (0, 0)')

    x_interval = grouped_not_zero['avg_offer']
    y_interval = grouped_not_zero['acceptance_ratio_per_interval']
    plt.scatter(x_interval, y_interval, color='black', label='Interval Average Value')

    print("Positive Model Summary:")
    print(positive_model.summary())

    print("\nNegative Model Summary:")
    print(negative_model.summary())

    plt.xlabel('Log Wage Difference')
    plt.ylabel('Acceptance (1 or 0)')
    plt.legend()

    filename_prefix = 'exclude do not know yet (642 offers)' if exclude_option == 1 else 'include do not know yet (908 offers)'
    plt.title(f'Acceptance Ratio on Log Wage Difference\n {filename_prefix}')
    plt.grid(True)
    
    # Save the plot with a specific filename based on option
    
    plot_filename = os.path.join(result_folder, f"{filename_prefix}_graph.jpg")
    plt.savefig(plot_filename, bbox_inches='tight', pad_inches=0.5)
    plt.show()
    plt.close()

    
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
file_paths = ['data/preprocessed_exclude_dk.csv', 'data/preprocessed_include_dk.csv']

# Folder name for saving results
result_folder = 'result'

# Check if the 'result' folder exists, if not, create it
if not os.path.exists(result_folder):
    os.makedirs(result_folder)

# Iterate through file paths
for file_path in file_paths:
    
    # Load the DataFrame and process outliers
    df = process_outliers(file_path) 
    
    # Setting the exclude option 
    if file_path == 'data/preprocessed_exclude_dk.csv' :
        exclude_option = 1 
    else:
        exclude_option = 2
        
    # Group the data
    grouped_not_zero, grouped_zero = group_data_quantile_bins(df, exclude_option)
    print(len(df), "exclude_option is ",exclude_option)
    
    # Total Table 
    total_table = grouped_not_zero.append(grouped_zero, ignore_index=True)

    
    # Extract filename without extension
    filename_prefix = os.path.splitext(os.path.basename(file_path))[0]
    
    # Save line graph and table CSV in the 'result' folder
    generate_and_save_final_graph(df, exclude_option)
    save_table_csv(total_table, filename_prefix, result_folder)

    


