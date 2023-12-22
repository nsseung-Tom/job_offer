import pandas as pd


def load_data(entry_file_path, weekly_file_path):
    df_entry = pd.read_stata(entry_file_path)
    df_weekly_rd = pd.read_stata(weekly_file_path)
    df_weekly = df_weekly_rd.loc[:,['caseid',
                     'curweek',
                     'curyear',
                     'startday',
                     'starttime',
                     'stopday',
                     'stoptime',
                     'extended_study',
                     'q7e',
                     'q7a1',
                     'q7a2',
                     'q12_1_a',
                     'q12_1_b',
                     'q13_1_a',
                     'q13_1_b1',
                     'q13_1_c',
                     'q14_1',
                     'q15_1',
                     'q13_2_a',
                     'q13_2_b1','q13_2_c']]
    return df_entry, df_weekly


def rename_columns(df):
    new_column_names = {
        'caseid':'caseid' ,
        'curweek':'curweek' ,
        'curyear':'curyear' ,
        'startday':'startday' ,
        'starttime':'starttime' ,
        'stopday':'stopday' ,
        'stoptime':'stoptime' ,
        'extended_study':'extended_study' ,
        'q7e':'how_many_hours_prefer_to_work_weekly' , 
        'q7a1':'reservation_wage' , 
        'q7a2':'reservation_unit' , 
        'q12_1_a':'received_job_offers' , 
        'q12_1_b':'how_many_job_offers' , 
        'q13_1_a':'job_offer_wage' , 
        'q13_1_b1':'job_offer_unit' , 
        'q13_1_c':'weekly_working_hour' , 
        'q14_1':'acceptance_yn' , 
        'q15_1':'reject_reason' , 
        'q13_2_a':'accepted_job_wage' , 
        'q13_2_b1':'accepted_job_unit' , 
        'q13_2_c':'accepted_weekly_working_hour' 
        }
    df = df.rename(columns=new_column_names)
    return df

# Filter data with valid job offer wage only
def filter_data(df):
    df_filtered = df[(df['job_offer_wage'].notnull())]
    return df_filtered


def generate_previous_reservation_wage(df):
    # Sort the DataFrame by 'caseid', 'curyear', and 'curweek'
    df.sort_values(by=['caseid', 'curyear', 'curweek'], inplace=True)

    # Get previous week's reservation_wage and reservation_unit for each caseid
    df['prev_reservation_wage'] = df.groupby('caseid')['reservation_wage'].shift()
    df['prev_reservation_unit'] = df.groupby('caseid')['reservation_unit'].shift()

    # For the first row of each caseid, use its own reservation_wage
    first_rows_mask1 = df['prev_reservation_wage'].isnull()
    first_rows_mask2 = df['prev_reservation_unit'].isnull()
    df.loc[first_rows_mask1, 'prev_reservation_wage'] = df.loc[first_rows_mask1, 'reservation_wage']
    df.loc[first_rows_mask2, 'prev_reservation_unit'] = df.loc[first_rows_mask2, 'reservation_unit']

    df_weekly_sum = df[(df['prev_reservation_wage'].notnull())]
    
    return df_weekly_sum


def calculate_hourly_wage(df, hours_column, wage_column, unit_column, output_column):
    def calculate(row):
        hours_worked_weekly = row[hours_column]
        reservation_wage = row[wage_column]
        reservation_unit = row[unit_column]
        
        if hours_worked_weekly == 0:
            # Handle cases where hours_worked_weekly is zero to avoid ZeroDivisionError
            return None

        if reservation_unit in [1, 'Year', 'year']:  # Yearly or 'year'
            hourly_wage = reservation_wage / (hours_worked_weekly * 52)  # Assuming 52 weeks in a year
        elif reservation_unit in [2, 'Month', 'month']:  # Monthly
            hourly_wage = reservation_wage / (hours_worked_weekly * 4)  # Assuming 4 weeks in a month
        elif reservation_unit in [3, 'Week', 'week', ' Week'] or reservation_unit in ['every two weeks', 'Every two week']:  # Weekly or 'every two weeks'
            if reservation_unit in ['every two weeks', 'Every two week']:
                hours_worked_weekly *= 2  # Doubling the hours for 'every two weeks' scenario
            hourly_wage = reservation_wage / hours_worked_weekly
        elif reservation_unit == 4 or reservation_unit == 'Hour' or reservation_unit == 'hour':  # Hourly or 'hour'
            hourly_wage = reservation_wage
        else:
            # Handle unrecognized reservation_unit values
            return None

        return hourly_wage

    df[output_column] = df.apply(calculate, axis=1)
    return df


def generate_hourly_wage_columns(df):
    # Previous_wage_hourly using Reservation Wage 
    df1= calculate_hourly_wage(df, 'how_many_hours_prefer_to_work_weekly', 'prev_reservation_wage', 'prev_reservation_unit', 'previous_wage_hourly')
    df2 = calculate_hourly_wage(df1, 'weekly_working_hour', 'job_offer_wage', 'job_offer_unit', 'job_offer_wage_hourly')
    df3 = calculate_hourly_wage(df2, 'accepted_weekly_working_hour', 'accepted_job_wage', 'accepted_job_unit', 'accepted_job_wage_hourly')
    return df3


def data_filtering_option(df, option):
    if option == 'entire_data':
        # Option 1: Using entire data from df_weekly_sum3
        
        final_table = df.copy()
    elif option == 'until_first_accept':
        # Option 2: Using data until each caseid's first 'Yes' in received_job_offers
        
        # Add a new column 'row_number' and increment only when 'acceptance_yn' is 'Yes'
        df['row_number'] = (df['acceptance_yn'] == 'Yes').groupby(df['caseid']).cumsum() 
        
        # row_number == 0이거나, row_number = 1 이고, acceptance_yn = 'Yes'인 애들만 남기기
        final_table = df[(df['row_number'] == 0) | ((df['row_number'] == 1) & (df['acceptance_yn'] == 'Yes'))]
    else:
        print("Invalid option! Please provide 'option_1' or 'option_2'")
        final_table = pd.DataFrame()  # Return an empty DataFrame for invalid option
    
    return final_table



def transform_acceptance(df, option):
    # Create an initial final_df DataFrame with basic columns
    basic_columns = ['caseid','curweek','curyear','received_job_offers', 'how_many_job_offers']
    final_df = df[basic_columns].copy()

    if option == 'exclude_dontknow':
        # Option 1: Map 'Yes' to 'y' and 'No' to 'n'
        condition_1 = df['acceptance_yn'] == 'Yes'
        condition_3 = df['acceptance_yn'] == 'No'
        final_df.loc[condition_1, 'offered_wage'] = df.loc[condition_1, 'job_offer_wage_hourly']
        final_df.loc[condition_1, 'previous_wage'] = df.loc[condition_1, 'previous_wage_hourly']
        final_df.loc[condition_1, 'acceptance_yn'] = 'y'
        final_df.loc[condition_3, 'offered_wage'] = df.loc[condition_3, 'job_offer_wage_hourly']
        final_df.loc[condition_3, 'previous_wage'] = df.loc[condition_3, 'previous_wage_hourly']
        final_df.loc[condition_3, 'acceptance_yn'] = 'n'
    elif option == 'include_dontknow':
        # Option 2: Map 'Yes' to 'y', 'No' to 'n', and 'Do not know yet' to 'n'
        condition_1 = df['acceptance_yn'] == 'Yes'
        condition_3 = (df['acceptance_yn'] == 'No') | (df['acceptance_yn'] == 'Do not know yet')
        final_df.loc[condition_1, 'offered_wage'] = df.loc[condition_1, 'job_offer_wage_hourly']
        final_df.loc[condition_1, 'previous_wage'] = df.loc[condition_1, 'previous_wage_hourly']
        final_df.loc[condition_1, 'acceptance_yn'] = 'y'
        final_df.loc[condition_3, 'offered_wage'] = df.loc[condition_3, 'job_offer_wage_hourly']
        final_df.loc[condition_3, 'previous_wage'] = df.loc[condition_3, 'previous_wage_hourly']
        final_df.loc[condition_3, 'acceptance_yn'] = 'n'
    else:
        print("Invalid option! Please provide 'option_1' or 'option_2'")
        
    
    final_df = final_df[final_df['acceptance_yn'].notna()]
    return final_df


def generate_final_four_tables(df_hourly_wage): 
    options = [('entire_data', 'exclude_dontknow'), ('entire_data', 'include_dontknow'), ('until_first_accept', 'exclude_dontknow'), ('until_first_accept', 'include_dontknow')]
    dataframes = []
    for i, (opt1, opt2) in enumerate(options):
        option_stage_1 = data_filtering_option(df_hourly_wage.copy(), opt1)
        final_data = transform_acceptance(option_stage_1, opt2)
        dataframes.append((final_data, opt1, opt2))  # Including options with dataframes
    return dataframes

def save_dataframes_as_csv(dataframes):
    for i, (df, opt1, opt2) in enumerate(dataframes, start=1):
        file_name = f'preprocessed{i}_{opt1}_{opt2}.csv'
        df.to_csv(f'data/{file_name}', index=False)
        print(f'Final table {i} saved as {file_name}')
        
        


# Preprocessing the data with functions above. 
entry_file_path = 'data/entry.dta'
weekly_file_path = 'data/weekly20150129.dta'
df_entry, df_weekly = load_data(entry_file_path, weekly_file_path)
df_weekly = rename_columns(df_weekly)
df_weekly_filtered = filter_data(df_weekly)
df_weekly_sum = generate_previous_reservation_wage(df_weekly_filtered)
df_hourly_wage = generate_hourly_wage_columns(df_weekly_sum)
final_dfs = generate_final_four_tables(df_hourly_wage)
save_dataframes_as_csv(final_dfs)


# For data check
# final_df1 = final_tables[0][0]
# final_df2 = final_tables[1][0]
# final_df3 = final_tables[2][0]
# final_df4 = final_tables[3][0]
# print(len(final_df1))
# print(len(final_df2))
# print(len(final_df3))
# print(len(final_df4))
