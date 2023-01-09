import pandas as pd
import datetime
import os
import argparse

# Takes .csv files in source directory, changes the time format of the "Start" and "Stop" columns to timedelta format (hour:minute:second) and saves output with "formatted" added to name in a directory "Time_Formatted" inside the path directory

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string) 

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=dir_path, help="pass directory")
args = parser.parse_args()

format_dir = os.path.join(args.path + "/Time_Formatted/") 
if not os.path.exists(format_dir):
    os.makedirs(format_dir)

for file in os.scandir(args.path):
    # Only works with csv files
    if file.path.endswith(".csv"):
        name = (os.path.basename(file.path))
        df = pd.read_csv(file.path)
        df['Start_formatted'] = df['Correct_start'].apply(lambda x: datetime.timedelta(seconds=x))
        df['Stop_formatted'] = df['Correct_stop'].apply(lambda x: datetime.timedelta(seconds=x))
        df = df[["Cumulative_shifted", "Correct_start", "Correct_stop", "Episode_order", "Season", "Episode", "Start_formatted", "Stop_formatted", "Speaker"]]

        path = os.path.join(format_dir + "Formatted_" + name)
        df.to_csv(path)


