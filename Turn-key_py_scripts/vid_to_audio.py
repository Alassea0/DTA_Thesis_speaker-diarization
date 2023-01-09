import os
import subprocess
import argparse

# Creates audio folder within video folder, puts .mp4 equivalent of video files in said audio folder

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=dir_path, help="pass directory")

args = parser.parse_args() 


def extract_audio(video_folder):
    # Make Audio folder inside video folder
    audio_folder = os.path.join(video_folder + "/Audio/") 

    # Check if the audio folder exists, create it if it doesn't
    if not os.path.exists(audio_folder):
      os.makedirs(audio_folder)
    
    for video_file in os.scandir(video_folder):
      # Select only video files
      if video_file.path.endswith('.mp4') or video_file.path.endswith('.mkv') or video_file.path.endswith('.avi'):

        audio_file = os.path.join(audio_folder, os.path.splitext(os.path.basename(video_file))[0] + 'audio.mp4')
        print(audio_file)
        subprocess.run(['ffmpeg', '-i', video_file, '-y', '-c', 'copy', '-map', '0:a', '-f', 'mp4', audio_file])


extract_audio(args.path)