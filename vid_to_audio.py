from pydub import AudioSegment
import os
import subprocess
import sys
import ffmpeg

# Make paths for needed folders

def make_audio_path(folder):
    """ Make paths for all Audio files of TV shows in a folder"""
    # Create empty path names list
    path_names = []
    for file in os.scandir(folder):
        # Append path name for TV show + Video
        path_names.append(os.path.join(file.path + "/Audio"))
    return path_names

def make_video_path(folder):
    """ Make paths for all Video files of TV shows in a folder"""
    # Create empty path names list
    path_names = []
    for file in os.scandir(folder):
        # Append path name for TV show + Video
        path_names.append(os.path.join(file.path + "/Video"))
    return path_names


tv_shows = '/home/ada/Documents/DTA/Thesis/Data/TV_shows/'
Men = tv_shows + 'Men/'
Women = tv_shows + 'Women/'

# Men
audio_paths_Men = make_audio_path(Men)
video_paths_Men = make_video_path(Men)

# Women
audio_paths_Women = make_audio_path(Women)
video_paths_Women = make_video_path(Women)



def extract_audio(video_folders, audio_folders):
  # Iterate over the video folders and extract the audio from all the video files
  for video_folder, audio_folder in zip(video_folders, audio_folders):
    # Check if the audio folder exists, create it if it doesn't
    if not os.path.exists(audio_folder):
      os.makedirs(audio_folder)

    # Get the list of video files in the video folder
    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith('.mp4') or f.endswith('.mkv') or f.endswith('.avi')]

    # Iterate over the video files and extract the audio
    for video_file in video_files:
      print(video_file)
      audio_file = os.path.join(audio_folder, os.path.splitext(os.path.basename(video_file))[0] + 'audio.mp4')
      subprocess.run(['ffmpeg', '-i', video_file, '-y', '-c', 'copy', '-map', '0:a', '-f', 'mp4', audio_file])


extract_audio(video_paths_Men, audio_paths_Men)
extract_audio(video_paths_Women, audio_paths_Women)