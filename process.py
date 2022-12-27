#!/usr/bin/python3

from pyannote.audio import Pipeline
import pickle
import numpy as np
import os
import subprocess
import copy
import pandas as pd
import re
import tempfile
import sys
import torch

torch.set_num_threads(int(sys.argv[3]))

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token="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")

def hook(step_name, step_artefact, file):
  print(f"File: {file}, Step name: {step_name}, Artefact type: {type(step_artefact)}")
  dst = sys.argv[2]
  if step_name == "embeddings":
    np.savez_compressed(dst + ".embt", step_artefact)
    sys.exit(0)
  if step_name == "segmentation":
    pickle.dump(step_artefact, open(dst + ".seg", "wb"))
  if step_name == "speaker_counting":
    pickle.dump(step_artefact, open(dst + ".sc", "wb"))

def progressSeg(parts, total):
    print("Segmentation",sys.argv[1],":",parts,"/",total)
    sys.stdout.flush()

pipeline._segmentation.progress_hook = progressSeg

pipeline(sys.argv[1], hook=hook)
