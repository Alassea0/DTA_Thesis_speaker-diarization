import pandas as pd
import datetime
import os
import argparse

# Takes .csv files in source directory, changes the time format of the "Start" and "Stop" columns to timedelta format (hour:minute:second) and saves output with "formatted" added to name

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=dir_path, help="pass directory")
args = parser.parse_args()


for file in os.scandir(args.path):
    # Only works with csv files
    if file.path.endswith(".csv"):
        name = (os.path.basename(file.path))
        df = pd.read_csv(file.path)
        df['Start_formatted'] = df['Start'].apply(lambda x: datetime.timedelta(seconds=x))
        df['Stop_formatted'] = df['Stop'].apply(lambda x: datetime.timedelta(seconds=x))
        df.to_csv(args.path + "formatted" + name)