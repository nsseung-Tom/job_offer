# Data on Job Offers

This repository contains data preprocessing scripts and data visualization for job offer data sourced from the NLSY79 dataset.

## Table of Contents

- [Introduction](#introduction)
- [Data Preprocessing](#data-preprocessing)
- [Data Visualization](#data-visualization)
- [File Structure](#file-structure)
- [Usage](#usage)
- [Codebook](#codebook)


## Introduction

The repository contains Python scripts for preprocessing raw job offer data and visualizing the processed data for analysis. The data is sourced from the NLSY79 dataset and focuses on job offers, acceptance, rejection, and wage differences.

## Data Preprocessing

### Preprocessing Raw Data

The `preprocess_raw_data.py` script reads the raw data from NLSY79, performs column name changes, and filters the data based on specific criteria related to job offers, rejection, and valid wage information.

### Preprocessing Functions

Two main preprocessing functions:
- `prev_wage_processing`: Processes previous wage information based on different options.
- `offered_wage_processing`: Processes offered wage information based on different options.

The resulting preprocessed data is saved in CSV files based on different combinations of preprocessing options.

## Data Visualization

The `data_visualization.py` script processes the preprocessed data, handles outliers, groups data into intervals, and generates visualizations in the form of line graphs to showcase acceptance ratios within wage difference intervals.

## File Structure

- /data
  - raw_data.csv
  - preprocessed_job2_wage_per_hr_only.csv
  - preprocessed_job2_wage_convert_to_hr.csv
  - preprocessed_prev_cps_wage_per_hr_only.csv
  - preprocessed_prev_cps_wage_convert_to_hr.csv
- /result
  - *_graph.jpg (Generated line graphs)
  - *_grouped_data.csv (Grouped data tables)
- preprocess_raw_data.py
- data_visualization.py

## Usage

To use the scripts:
1. Update the file paths as needed.
2. Run `preprocess_raw_data.py` with appropriate options for data preprocessing.
3. Run `data_visualization.py` to generate visualizations based on preprocessed data.


## Codebook

| Variable    | Question Name                                                  | Description                                                      | Year | Corresponding Column in Data     |
|-------------|----------------------------------------------------------------|------------------------------------------------------------------|------|----------------------------------|
| R0000100    | CASEID                                                         | IDENTIFICATION CODE                                               | 1979 | case_id                          |
| R0173600    | SAMPLE_ID                                                      | SAMPLE IDENTIFICATION CODE                                        | 1979 | sample_id                        |
| R0214700    | SAMPLE_RACE                                                    | R'S RACIAL/ETHNIC COHORT FROM SCREENER                            | 1978 | sample_race                      |
| R0214800    | SAMPLE_SEX                                                     | SEX OF R                                                          | 1979 | sample_sex                       |
| R0263710    | CPSHRP                                                         | HOURLY RATE OF PAY CURRENT/MOST RECENT JOB                       | 1980 | 1980_cps_wage                    |
| R0446810    | CPSHRP                                                         | HOURLY RATE OF PAY CURRENT/MOST RECENT JOB                       | 1981 | 1981_cps_wage                    |
| R0702510    | CPSHRP                                                         | HOURLY RATE OF PAY CURRENT/MOST RECENT JOB                       | 1982 | 1982_cps_wage                    |
| R0709400    | SRCH-7                                                         | METHOD OF FINDING MOST RECENT JOB - WORKING WHEN 1ST OFFERED A JOB? | 1982 | working_when_offered             |
| R0709500    | SRCH-8                                                         | METHOD OF FINDING MOST RECENT JOB - LOOKING FOR WORK WHEN OFFERED JOB | 1982 | looking_for_job                  |
| R0712100    | SRCH-23                                                        | METHOD OF FINDING MOST RECENT JOB - ANY JOB OFFERS R DID NOT TAKE? | 1982 | any_job_offers_did_not_take     |
| R0712200    | SRCH-24                                                        | METHOD OF FINDING MOST RECENT JOB - # OF JOB OFFERS R DID NOT TAKE | 1982 | num_of_job_offers_did_not_take  |
| R0712300    | SRCH-25                                                        | METHOD OF FINDING MOST RECENT JOB - RATE OF PAY OF BEST JOB OFFER REJECTED | 1982 | best_wage_rejected               |
| R0712400    | SRCH-26                                                        | METHOD OF FINDING MOST RECENT JOB - TIME UNIT RATE OF PAY OF BEST JOB REJECTED | 1982 | time_unit_of_rejected_wage       |
| R0712500    | SRCH-27                                                        | METHOD OF FINDING MOST RECENT JOB - REASON R DID NOT ACCEPT BEST JOB OFFER | 1982 | reason_for_rejection             |
| R0833200    | EMPLOYER_STARTDATE.01~M                                        | MONTH BEGAN WORKING (OR LAST INT IF BEFORE THEN) JOB #01          | 1982 | month_began_working_1982_cps    |
| R0833400    | EMPLOYER_STARTDATE.01~Y                                        | YEAR BEGAN WORKING (OR LAST INT IF BEFORE THEN) JOB #01           | 1982 | year_began_working_1982_cps     |
| R0840100    | QES-52.01                                                      | INT CHECK 82 - IS JOB #01 SAME AS CURRENT JOB?                    | 1982 | is_job1_cps                     |
| R0841010    | HRP1                                                           | HOURLY RATE OF PAY JOB #01                                        | 1982 | hourly_wage_of_job1             |
| R0854110    | HRP2                                                           | HOURLY RATE OF PAY JOB #02                                        | 1982 | hourly_wage_of_job2             |
| R0896711    | DOI_EMPLOYED                                                   | DATE OF INTERVIEW STATUS - EMPLOYED                                | 1982 | employed_status                  |
