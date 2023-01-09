import pandas as pd
from sklearn.metrics import adjusted_rand_score 
import argparse
import os

# Prints adjusted rand index (ARI) for TV show where an error analysis has been done. It requires for the Error Analysis column to be named "Actual", this must be done manually
# Prints ARI for TV shows excluding the "None"s
# Prints the total number of utterances in a TV show
# Prints the amount of utterances used in the error analysis (amount of rows filled in in "Actual")

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=argparse.FileType('r'))
args = parser.parse_args()

df = pd.read_csv(args.file)


df = df[['Speaker', 'Actual']]
filtered_df = df[df['Actual'].notnull()]
no_none = filtered_df.drop(filtered_df[filtered_df.Actual == "none"].index)
no_none = no_none.drop(no_none[no_none.Actual == "None"].index)

speaker = filtered_df['Speaker'].tolist()
actual = filtered_df['Actual'].tolist()
all = adjusted_rand_score(speaker, actual)
print(f"The Adjusted Rand Score is {all}")


speaker = no_none['Speaker'].tolist()
actual = no_none['Actual'].tolist()
without_none = adjusted_rand_score(speaker, actual)
print(f"The Adjusted Rand Score excluding 'None' is {without_none}")
print(f"The total number of utterances for this TV show is {len(df)}")
print(f"The number of utterances used for the Error Analysis is {len(filtered_df)} ")