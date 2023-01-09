# Speaker Diarization tool for Consecutive Audio Files

The following tool creates a speaker diarization file for consecutive audio files from TV shows, with consistent speaker tags throughout the TV show.

To do this, it first extracts speaker embeddings, segmentations and speaker counts from each episode with [pyannote.audio](https://github.com/pyannote/pyannote-audio)'s speaker diarization model, then it merges the files into one, at which point the clustering step from pyannote's speaker diarization model is applied to the merged file. After the clustering is done, it then separates the file per episode, puts them in the correct order and assigns the episode season and number to each episode. The file is then once again merged into one, so the output is a single csv file per TV show. This file can then be used to perform social network analysis on the TV shows.

### Social Network for the TV show Bridgerton
<img src="/Images/Bridgerton_network.png" width="500">

---
## How to apply
In order to use the tool, the following commands must be run on the terminal\footnote{These commands are specific to a Linux Debian system, changes may need to be made for Mac or Windows systems.}:

Converting video files to audio files:
```console
foo@bar:~$ python vid_to_audio.py -p path_to_source_directory
```

Building the dockerfile so pyannote can easily be used on any system. This command only needs to be run one time on a computer system:
```console
foo@bar:~$ docker build . -t pyannote
```

Extracting the speaker embeddings, speaker segmentations and speaker count files from all episodes. In this command, 2 is the number of simultaneous episodes to be processed and 3 is the number of cores to be used per episode:
```console
foo@bar:~$ sudo docker run -it -v `pwd`/path_to_source_directory:/audio pyannote 2 3
```

Combining the files, clustering and separating per episode. The name of the TV show that is being processed must be entered for the file name: 
```console
foo@bar:~$ sudo docker run -it -v `pwd`/path_to_source_directory:/audio -v `pwd`/Results:/results --entrypoint=/app/clustering_show.py pyannote /audio /results/ "TV_show_name"
```

Processing the resulting \verb|.csv| file:
```console
foo@bar:~$ python process_csv.py -p path_to_source_directory
```

Changing format of the \verb|.csv| file:
```console
foo@bar:~$ python change_time_format.py -p path_to_source_directory
```

The previous commands will result in one \verb|.csv| file per TV show, ready for the error analysis, as the time format has been changed from seconds to hour:minute:second. Once the manual error analysis has been done, the following commands can be run on the resulting file.

Get adjusted rand index for the error analysis, as well as the total number of utterances in a TV show, and the number of utterances used for the error analysis:
```console
foo@bar:~$ python get_adjusted_rand_index.py -f path_to_file
```

Extract a \verb|.gexf| file from the \verb|.csv| file. This file can then be used to visualize the network in \textit{Gephi}.
```console
foo@bar:~$ python csv_to_gexf.py -p path_to_source_directory
```
