from pyannote.audio import Pipeline
import pickle
import numpy as np
import os
import subprocess
import copy
import pandas as pd
import re
import sys

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                    use_auth_token="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")


##### CREATE PATHS #####

def create_paths(directory):
  """ 
  Creates empty lists for embeddings, segmentation and speaker counts of each episode
  """
  embed = []
  segment = []
  speakers = []

  # Scanning video folder directory and adding file paths in their corresponding lists
  for file in os.scandir(directory):
    # Only works with wav files
    if file.path.endswith(".sc"):
      f = file.path
      f = f[:-3]
      embed.append(f + ".emb.npz")
      segment.append(f + ".seg")
      speakers.append(f + ".sc")
  return embed, segment, speakers

##### EMBEDDINGS #####


def load_embeddings_create_titles(embeddings_paths):
  """
  Loads embedding files and titles into a list (from paths made previously)
  """
  # Regex pattern to extract season and episode from episode titles (format "S01E01")
  pattern = "S([0-9]{2})E([0-9]{2})"
  embs = []
  titles = []
  for file in embeddings_paths:
    titles.append(re.search(pattern, file).group())
    emb = np.load(file)["arr_0"]
    embs.append(emb)
  return embs, titles

def create_cut_points(embs):
  """
  Makes a list of the lengths of each episode, as well as the cut points between episodes, so we can separate them again later
  """
  index = 0
  cut_points = []
  for element in embs:
    index += len(element)
    cut_points.append(index)
  return cut_points

##### SEGMENTATION AND SPEAKER COUNT #####


def concat_windows(l1,l2):
  """ 
  Concatenates SlidingWindowFeature type data
  """
  l1.data = np.concatenate((l1.data, l2.data))
  return l1


def combine_all_old(files):
  """
  Concatenates all elements in a list of SlidingWindowFeatures 
  """
  combo = copy.copy(files[0]) # Making a copy to avoid overwriting the original [0] file with the combo
  i = 0
  while i < (len(files)-1):
    for element in files[1:]:
      combo = concat_windows(combo, element)
      i += 1
  return combo

def combine_all(files):
  """
  Concatenates all elements in a list of SlidingWindowFeatures 
  """
  i = 0
  combo = copy.copy(files[0]) # Making a copy to avoid overwriting the original [0] file with the combo
  for element in files[1:]:
    combo = concat_windows(combo, element)
    print("append", i, len(files), len(combo.data))
    i+=1
  
  return combo


def load_files(paths):
  """
  Loads segmentation files into a list (from paths made previously)
  """
  l = []
  for file in paths:
    with open(file, "rb") as f:
      done = pickle.load(f)
      l.append(done)
  return l

##### GET EPISODE LENGTH AND CUT POINTS IN SECONDS #####

def get_ep_length_and_cutpts(segment_list, cut_points):
  """
  Returns two lists:
  1. A list of the length of all episodes in seconds
  2. A list of the cut points (which we need to use to separate the episodes) in seconds
  """

  ep_lengths = []
  cut_points_seconds = []

  for window in segment_list:
    total = len(window)
    step = window.sliding_window.step
    dur = window.sliding_window.duration
    length = (total * step + dur) 
    ep_lengths.append(length)

  for f in cut_points:
    step = segment_list[0].sliding_window.step
    dur = segment_list[0].sliding_window.duration
    length = (f * step + dur)
    cut_points_seconds.append(length)

  return ep_lengths, cut_points_seconds


##### CLUSTERING #####

from pyannote.audio.pipelines.clustering import Clustering
from pyannote.audio.pipelines.speaker_diarization import SpeakerDiarization
from pyannote import core
from pyannote.audio.utils.signal import binarize


def reconstructed_clustering(segmentation, embeddings, speaker_count, max_clusters=35):
  """
  Based on code from pyannote github: https://github.com/pyannote/pyannote-audio/blob/develop/pyannote/audio/pipelines/speaker_diarization.py
  Performs clustering step of the pyannote speaker diarization pipeline on segmentation, embedding and speaker count files
  """
  clustering = Clustering["HiddenMarkovModelClustering"].value(metric = "cosine")
  clustering.covariance_type = "diag"
  clustering.threshold = 0.35
  
  binarized_segmentations: core.SlidingWindowFeature = binarize(
            segmentation,
            onset=0.58,
            initial_state=False,
        )
  
  hard_clusters, _ = clustering(
            embeddings = embeddings,
            segmentations = binarized_segmentations,
            #num_clusters=25,
            min_clusters=25,
            max_clusters=max_clusters,
            )
  # keep track of inactive speakers
  inactive_speakers = np.sum(binarized_segmentations.data, axis=1) == 0
  
  # shape: (num_chunks, num_speakers)
  hard_clusters[inactive_speakers] = -2
  discrete_diarization = pipeline.reconstruct(
      segmentations = segmentation,
      hard_clusters = hard_clusters,
      count = speaker_count,
      )
  
  # convert to continuous diarization
  diarization = pipeline.to_annotation(
      discrete_diarization,
      min_duration_on = 0.0,
      min_duration_off = 0.0,
      )
  
  return diarization

##### CREATE DF FROM DIARIZATION #####

def df_from_dia(diarization):
  """
  Gets dataframe from diarization output: start second, end second and speaker
  """
  start = []
  stop = []
  speakers = [] 
  for turn, _, speaker in diarization.itertracks(yield_label=True):
    start.append(turn.start)
    stop.append(turn.end)
    speakers.append(speaker)
  
  list_of_tuples = list(zip(start, stop, speakers))
  
  df = pd.DataFrame(list_of_tuples, columns = ["Start", "Stop", "Speaker"])

  return df

##### EVERYTHING TOGETHER #####

def diarize_and_cluster(directory):
  """
  Combines all functions to diarize and cluster all episodes in a directory
  """
  # Create paths to all files we need
  embed_paths, segment_paths, speakers_paths = create_paths(directory)

  # Load embeddings into list, create list of titles
  embed_list, titles = load_embeddings_create_titles(embed_paths)
  # Create cut points from embedding list
  cut_points = create_cut_points(embed_list)
  # Concatenating all embedding arrays into one
  embeddings = np.concatenate(embed_list)
  
  # Load segmentations into list
  segment_list = load_files(segment_paths)
  # Concatenating all segmentation SlidingWindowFeature files
  segmentation = combine_all(segment_list)
  
  # Load speakers into list
  speaker_list = load_files(speakers_paths)
  # Concatenating all speaker count SlidingWindowFeature files
  speaker_count = combine_all(speaker_list)
  
  # Get episode lengths and cut points in seconds, both into a list
  ep_lengths, cut_points_seconds = get_ep_length_and_cutpts(segment_list, cut_points)

  # Cluster all episodes
  diarization = reconstructed_clustering(segmentation, embeddings, speaker_count)

  # Put diarization into dataframe
  df = df_from_dia(diarization)

  return df, cut_points_seconds, titles, ep_lengths

#### SPLIT DF INTO EPISODES AND EXPORT CSV ####

def create_index_list(cut_points_seconds, df):
  """
  Creates an index list to cut the dataframe based on cut points in seconds
  """
  index_list = []
  for second in cut_points_seconds:
    index = np.abs(df["Stop"] - second).argmin()
    index_list.append(index)

  return index_list

def split_dataframe(index_numbers, df, titles):
  """
  Splits dataframe into episodes based on index list, attaches title
  """
  df_list = []
  start_index = 0
  for end_index in index_numbers:
      df_list.append(df[start_index:end_index])
      start_index = end_index
  df_list.append(df[start_index:])
  df_dict = dict(zip(titles, df_list))

  return df_dict

def final_all(directory):
  df, cut_points_seconds, titles = diarize_and_cluster(directory)
  index_list = create_index_list(cut_points_seconds, df)
  df_dict = split_dataframe(index_list, df, titles)
  return df_dict, titles

def save_csv(df_dict, ep_lengths, directory, show_title):
  order = []
  for (title, df), ep_length in zip(df_dict.items(), ep_lengths):
    df['Season'] = title[2]
    df['Episode'] = title[4:]
    df['Episode_order'] = title[2] + title[4:]
    df['ID'] = title
    df['Episode_length'] = ep_length
    order.append(df['Episode_order'].iloc[1])	
  order = sorted(order)
  sorted_df_dict = dict(sorted(df_dict.items(), key=lambda x: order.index(x[1]['Episode_order'].iloc[0])))
  merged = pd.concat(sorted_df_dict.values(), ignore_index=True)
  merged.to_csv(directory + show_title + ".csv")
  return merged


def remove_spaces(directory):
    [os.rename(os.path.join(directory, f), os.path.join(directory, f).replace(" ", "_")) for f in os.listdir(directory)]

def remove_doubles(directory):
    [os.rename(os.path.join(directory, f), os.path.join(directory, f).replace("..", ".")) for f in os.listdir(directory)]


remove_spaces(sys.argv[1])
remove_doubles(sys.argv[1])

df_dict, titles, ep_lengths = final_all(sys.argv[1])
final = save_csv(df_dict, ep_lengths, sys.argv[2], sys.argv[3])

# sys.argv[1] = source directory
# sys.argv[2] = destination directory
# sys.argv[3] = TV show name

# Commands:
# python clustering_show.py ./Men/The_Punisher ./Clustered_final "The Punsiher"
# python clustering_show.py ./Men/The_Wire ./Clustered_final "The Wire"
# python clustering_show.py ./Men/Spartacus ./Clustered_final Spartacus
# python clustering_show.py ./Men/Narcos ./Clustered_final Narcos

# python clustering_show.py ./Women/Gossip_Girl ./Clustered_final "Gossip_Girl"
# python clustering_show.py ./Women/Bridgerton ./Clustered_final Bridgerton
# python clustering_show.py ./Women/Jane_the_Virgin ./Clustered_final "Jane the Virgin"
# python clustering_show.py ./Women/Pretty_Little_Liars ./Clustered_final "Pretty Little Liars"
