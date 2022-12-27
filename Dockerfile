FROM ubuntu:22.04

RUN apt -y update \
    && apt -y --no-install-recommends install build-essential python3-pip libsndfile-dev ffmpeg python3-dev libxml2-dev libxslt-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install torch==1.11.0+cu102 torchvision==0.12.0+cu102 torchaudio==0.11.0 torchtext==0.12.0 --extra-index-url https://download.pytorch.org/whl/cu102 pyannote.audio sndfile \
    && python3 -c "from pyannote.audio import Pipeline;Pipeline.from_pretrained(\"pyannote/speaker-diarization@2.1\", use_auth_token=\"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\")"

WORKDIR /app
COPY app/* /app/

ENTRYPOINT ["/app/process_folder.sh"]
