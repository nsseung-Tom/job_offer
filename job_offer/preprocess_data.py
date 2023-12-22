import numpy as np 
import pandas as pd

# Read the CSV file into a pandas DataFrame
file_path = 'data/raw_data.csv'  # File path (change if needed)
df = pd.read_csv(file_path)

# New column names
new_columns = [
    'case_id', 'sample_id', 'sample_race', 'sample_sex', '1980_cps_wage',
    '1981_cps_wage', '1982_cps_wage', 'working_when_offered', 'looking_for_job',
    'any_job_offers_did_not_take', 'num_of_job_offers_did_not_take',
    'best_wage_rejected', 'time_unit_of_rejected_wage', 'reason_for_rejection',
    'month_began_working_1982_cps', 'year_began_working_1982_cps', 'is_job1_cps',
    'hourly_wage_of_job1', 'hourly_wage_of_job2', 'employed_status'
]

# Change column names
if len(df.columns) == len(new_columns):
    df.columns = new_columns
    print("Column names changed successfully!")
else:
    print("Number of new column names doesn't match the number of existing columns.")

# Common filtering operations
df_pro = df[(df["num_of_job_offers_did_not_take"] == 1) & (df["looking_for_job"] == 1) & (df["any_job_offers_did_not_take"] == 1)]
df_processed = df_pro[(df_pro['1982_cps_wage'] > 0) & (df_pro['best_wage_rejected'] > 0) & (df_pro['is_job1_cps'] == 1)]


def preprocess_data(data, prev_wage_option, offered_wage_option):
    processed_stage_1 = prev_wage_processing(data, prev_wage_option)
    processed_stage_2 = offered_wage_processing(processed_stage_1, offered_wage_option)
    final_data = create_final_data(processed_stage_2)
    return final_data


def prev_wage_processing(data, prev_wage_option):
    if prev_wage_option == 'job2_wage':
        processed_data = data[data['hourly_wage_of_job2'] > 0]
        processed_data.loc[:, 'previous_wage'] = processed_data['hourly_wage_of_job2']
    elif prev_wage_option == 'prev_cps_wage':
        data['previous_wage'] = data.apply(
            lambda x: x['1981_cps_wage'] if x['year_began_working_1982_cps'] == 82
            else (x['1980_cps_wage'] if x['year_began_working_1982_cps'] == 81 else np.nan),
            axis=1
        )
        processed_data = data[data['previous_wage'] > 0]
    else:
        raise ValueError("Invalid stage 1 option selected.")
    return processed_data


def offered_wage_processing(data, offered_wage_option):
    if offered_wage_option == 'per_hr_only':
        processed_data = data[data['time_unit_of_rejected_wage'] == 1]
        processed_data.loc[:, 'best_wage_rejected_hr'] = processed_data['best_wage_rejected']
    elif offered_wage_option == 'convert_to_hr':
        data['best_wage_rejected_hr'] = data.apply(adjust_to_hourly, axis=1)
        processed_data = data
    else:
        raise ValueError("Invalid stage 2 option selected.")
    return processed_data


def adjust_to_hourly(row):
    wage = row['best_wage_rejected']
    time_unit = row['time_unit_of_rejected_wage']
    if time_unit == 1:  # Per hour
        return wage
    elif time_unit == 2:  # Per day
        return wage / 8  # Assuming 8 hours per day
    elif time_unit == 3:  # Per week
        return wage / (8 * 5)  # Assuming 8 hours per day and 5 days per week
    elif time_unit == 5:  # Per month
        return wage / (8 * 5 * 4)  # Assuming 8 hours per day, 5 days per week, and 4 weeks per month
    elif time_unit == 6:  # Per year
        return wage / (8 * 5 * 52)  # Assuming 8 hours per day, 5 days per week, and 52 weeks per year
    else:
        return -100  # If time unit is not recognized, return the minus value (not valid)


def create_final_data(processed_stage_2):
    new_data = []
    for index, row in processed_stage_2.iterrows():
        case_id = row['case_id']
        sample_id = row['sample_id']
        sample_race = row['sample_race']
        sample_sex = row['sample_sex']
        offered_wage = row['1982_cps_wage']
        previous_wage = row['previous_wage']
        
        # For 'acceptance_yn = y' row  -> 1982 CPS is the accepted job offer 
        new_data.append({
            'case_id': case_id,
            'sample_id': sample_id,
            'sample_race': sample_race,
            'sample_sex': sample_sex,
            'offered_wage': offered_wage,
            'previous_wage': previous_wage,
            'acceptance_yn': 'y'
        })
        
        # For 'acceptance_yn = n' row -> In the 1982 survey, they offer the rejected job offer when they are looking for CPS job at that time.
        new_data.append({
            'case_id': case_id,
            'sample_id': sample_id,
            'sample_race': sample_race,
            'sample_sex': sample_sex,
            'offered_wage': row['best_wage_rejected_hr'],
            'previous_wage': previous_wage,
            'acceptance_yn': 'n'
        })

    final_data = pd.DataFrame(new_data)
    return final_data


def save_final_data(final_data, prev_wage_option, offered_wage_option):
    output_folder = 'data/'  # Folder path
    output_filename = f"{output_folder}preprocessed_{prev_wage_option}_{offered_wage_option}.csv"
    final_data.to_csv(output_filename, index=False)
    print("Length of final_data:", len(final_data))  # Print the length of final_data
    return output_filename


prev_wage_options = ['job2_wage', 'prev_cps_wage']
offered_wage_options = ['per_hr_only', 'convert_to_hr']

for opt_1 in prev_wage_options:
    for opt_2 in offered_wage_options:
        processed_data = preprocess_data(df_processed, opt_1, opt_2)
        saved_file = save_final_data(processed_data, opt_1, opt_2)
        print(f"File '{saved_file}' created for options '{opt_1}' and '{opt_2}'")