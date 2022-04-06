'''
This script is for generating a filler-data sample csv for use in a simple split-test analysis.
The column names and data types are designed to mimick a csv exported from Facebook Ads Manager.
User notes:
    - num_sets should be an integer between 1 and 26, inclusive (default 2)
    - num_messages should be an integer (default 8)
    - impressions_range should be a list of two integers, the desired floor and ceiling of the possible random numbers of
    impressions generated
    - clicks_range should be a list of two integers, the desired floor and ceiling of the possible random numbers of clicks
    generated
    - reach_percentage_range should be a list of two integers, the desired floor and ceiling of the possible random percentages
    of impressions the reach can be (reach means unique impressions)
    - uclicks_percentage_range should be a list of two integers, the desired floor and ceiling of the possible random percentages
    of the number of clicks the number of unique clicks can be (if the randomly generated number is larger than the reach for a
    given row, it will be replaced with the reach)
'''

import argparse
import pandas as pd
import random
import string
import json

FILENAME = 'filler_facebook_ad_data.csv'
REPORTING_STARTS = '2022-04-01'
REPORTING_ENDS = '2022-04-15'

def create_ad_set_names_list(num_sets: list, num_messages: list) -> list:
    alphabet = list(string.ascii_uppercase)
    set_names = [f'Set{letter}' for letter in alphabet[0:num_sets]]
    message_names = [f'M{num}' for num in range(1, num_messages + 1)]
    ad_set_names = []
    for set in set_names:
        for message in message_names:
            ad_set_names.append(f'{set} {message}')
    return ad_set_names

def create_impressions_clicks_list(size: int, floor: int, ceiling: int) -> list:
    values = []
    for _ in range(size):
        values.append(random.randint(floor, ceiling))
    return values

def create_reach_uclicks(num: int, floor: int, ceiling: int) -> int:
    pct = random.randint(floor, ceiling)/100
    result = int(num*pct)
    return result

def generate_csv(
    num_sets: int,
    num_messages: int,
    impressions_range: list,
    reach_percentage_range: list,
    clicks_range: list,
    uclicks_percentage_range: list
) -> None:
    df = pd.DataFrame()
    df['Ad Set Name'] = create_ad_set_names_list(num_sets=num_sets, num_messages=num_messages)
    df['Campaign Name'] = 'filler_data'
    df['Impressions'] = create_impressions_clicks_list(len(df), *impressions_range)
    df['Reach'] = df['Impressions'].apply(lambda x: create_reach_uclicks(x, *reach_percentage_range))
    df['Clicks (all)'] = create_impressions_clicks_list(len(df), *clicks_range)
    df['Unique clicks (all)'] = df['Clicks (all)'].apply(lambda x: create_reach_uclicks(x, *uclicks_percentage_range))
    df['Unique clicks (all)'] = \
        df.apply(lambda x: x['Reach'] if x['Unique clicks (all)'] > x['Reach'] else x['Unique clicks (all)'], axis=1)
    df['Reporting starts'] = REPORTING_STARTS
    df['Reporting ends'] = REPORTING_ENDS
    csv_content = df.to_csv(index=False)
    with open(FILENAME, 'w', newline='') as f:
        f.write(csv_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--impressions_range", required=True)
    parser.add_argument("--clicks_range", required=True)
    parser.add_argument("--reach_percentage_range", required=True)
    parser.add_argument("--uclicks_percentage_range", required=True)
    parser.add_argument("--num_sets", default=2)
    parser.add_argument("--num_messages", default=8)
    args = parser.parse_args()
    num_sets = args.num_sets
    num_messages = args.num_messages
    impressions_range = json.loads(args.impressions_range)
    clicks_range = json.loads(args.clicks_range)
    reach_percentage_range = json.loads(args.reach_percentage_range)
    uclicks_percentage_range = json.loads(args.uclicks_percentage_range)
    generate_csv(
        num_sets=num_sets,
        num_messages=num_messages,
        impressions_range=impressions_range,
        reach_percentage_range=reach_percentage_range,
        clicks_range=clicks_range,
        uclicks_percentage_range=uclicks_percentage_range
    )
