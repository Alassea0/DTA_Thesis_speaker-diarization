import pandas as pd
import networkx as nx
from itertools import combinations
import argparse
import os



def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=dir_path, help="pass directory")
args = parser.parse_args()

def create_gexf(directory):
    """
    Creates network from all .csv files in directory and saves .gexf file 
    """
    for file in os.scandir(directory):
        # Only works with csv files
        if file.path.endswith(".csv"):
            name = (os.path.basename(file.path))
            name = name[:-4]
            df = pd.read_csv(file.path)
            df['Speaker'] = df['Speaker'].astype(str)
            speaker_list = df['Speaker'].tolist()
            G = nx.Graph()
            si, ei = 0, 2 #start index, end index
            while ei < len(speaker_list):
                interaction = []
                for character in set(speaker_list[si : ei]):
                    if ' ' in character:
                        interaction.extend(character.split())
                    else:
                        interaction.append(character)
                interaction = set(interaction)
                if len(interaction) > 1:
                    for sp1, sp2 in combinations(interaction, 2):
                        if G.has_edge(sp1, sp2):
                            G[sp1][sp2]['weight'] += 1
                        else:
                            G.add_edge(sp1, sp2, weight=1)
                si += 1
                ei += 1
                
            nx.write_gexf(G, directory + name + '_network.gexf')

create_gexf(args.path)



 