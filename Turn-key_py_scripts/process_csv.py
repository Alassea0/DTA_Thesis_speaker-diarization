import pandas as pd
import os
import argparse

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)
 
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=dir_path, help="pass directory")

args = parser.parse_args() 


def process(directory):
    # Make Audio folder inside video folder
    processed_folder = os.path.join(directory + "/Processed/") 

    # Check if the audio folder exists, create it if it doesn't
    if not os.path.exists(processed_folder):
      os.makedirs(processed_folder)

    for file in os.scandir(directory):
        if file.path.endswith(".csv"):
            name = (os.path.basename(file.path))
            print(name)

            df = pd.read_csv(file.path)
            # Remove all speech segments shorter than 0.4s
            df = df[df['Stop'] - df['Start'] > 0.4]
            # Sorting by processing order instead of episode order
            df = df.sort_values(by=['Start'], ascending=True)
            # Saving processing order in column to sort data with later
            labels, _ = pd.factorize(df['ID'])
            df = df.assign(processing_order=labels)
            df = df.reset_index()

            # Make cumulative lengths column (sum of the lengths of all previously processed episodes) to subtract from Start and Stop for correct times
            cumulative = df.groupby(["Episode_length", "processing_order", "ID"], sort=False, as_index=False).count()
            # Sort by processing order so we can make a cumulative length column to subtract from the Start and Stop times
            cumulative = cumulative.sort_values(by=['processing_order'], ascending=True)
            cumulative['Cumulative_length'] = cumulative['Episode_length'].cumsum()
            cumulative = cumulative[['Cumulative_length', "ID"]]
            # Shift the cumulative length column down by one so the length of the first episode doesn't get subtracted from its Start and Stop times 
            cumulative['Cumulative_shifted'] = cumulative['Cumulative_length'].shift(+1)
            cumulative = cumulative.fillna(0)

            # Merge our dataframe with the comulative lengths column on ID to assign correct cumulative length value to each episode
            merged = pd.merge(df, cumulative, how="left", on=["ID"])

            # Save cumulative lengths into list so we can use them as bins to separate episodes correctly
            cumulative_list = cumulative['Cumulative_shifted'].tolist()
            # Appending final number to cumulative lengths list so the last episode gets stored in the correct bin
            cumulative_list.append(99999999.9)

            # Saving episode IDs to list so we can use them to make new IDs
            id_list = merged['ID'].unique().tolist()

            # Making new episode IDs with cumulative lengths list, episode IDs and Start column, so the boundaries between episodes are accurate
            merged['new_id'] = pd.cut(df['Start'],
                                        bins=cumulative_list,
                                        labels=id_list,
                                        right=False
                                        )


            # Rename episode ID in cumulative df so we can merge on new_id 
            cumulative["new_id"] = cumulative["ID"]
            cumulative_subset = cumulative[["Cumulative_shifted", "new_id"]]

            # Selecting only necessary columns
            simple_subset = merged[["Start", "Stop", "Speaker", "processing_order", "Episode_length", "new_id"]]

            # Merge on new episode ID, so cumulative length column gets assigned to correct episode boundaries
            merged2 = pd.merge(simple_subset, cumulative_subset, how="left", on=["new_id"])

            # Create new Correct Start and Stop times by subtracting length of all previously processed episodes
            merged2['Correct_start'] = merged2["Start"] - merged2["Cumulative_shifted"]
            merged2['Correct_stop'] = merged2["Stop"] - merged2["Cumulative_shifted"]

            # Making Season and Episode and Episode Order columns from new episode ID
            merged2["Season"] = merged2["new_id"].str[2]
            merged2["Episode"] = merged2["new_id"].str[4:]
            merged2["Episode_order"] = merged2["Season"] + merged2["Episode"]

            # Sort by Episode Order and Start to get episodes back in chronological order while keeping the correct order of the speech segments
            merged2 = merged2.sort_values(by=["Episode_order", "Start"], ascending=True)

            merged2 = merged2[["Cumulative_shifted", "Episode_order", "Season", "Episode", "Correct_start", "Correct_stop", "Speaker"]]


            path = os.path.join(processed_folder + "Processed_" + name)
            print(path)
            merged2.to_csv(path, index=False)
    
process(args.path)