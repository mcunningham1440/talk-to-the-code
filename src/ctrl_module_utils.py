import os
from pydub import AudioSegment
from scipy.io.wavfile import write

from config import *


def get_voice_transcript(voice_data, openai_client, recording_time):
    base_filename = os.path.join("temp_recordings", f"{recording_time}")
    wav_filename = base_filename + ".wav"
    mp3_filename = base_filename + ".mp3"

    print(os.getcwd())

    write(wav_filename, config.sampling_freq, voice_data)

    AudioSegment.from_wav(wav_filename).export(mp3_filename, format="mp3")

    os.remove(wav_filename)

    mp3_file = open(mp3_filename, "rb")

    transcript = openai_client.audio.transcriptions.create(
        file=mp3_file,
        model="whisper-1",
        language="en",
        response_format="text"
        )
        
    os.remove(mp3_filename)

    return transcript