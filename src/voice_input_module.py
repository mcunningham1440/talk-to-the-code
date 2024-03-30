import tkinter as tk
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
from datetime import datetime
from pydub import AudioSegment
from openai import OpenAI

from config import *

class VoiceInputModule:
    def __init__(self, root):
        self.root = root

        self.recording = False
        self.fs = 44100

        self.label = tk.Label(root, text="Transcribed_text")

        self.transcribed_text_display = tk.Text(root)
        self.transcribed_text_display.pack()

        self.record_button = tk.Button(root, text="Record", command=self._toggle_recording)
        self.record_button.pack()

        self.submit_button = tk.Button(root, text="Submit", state='disabled', command=self._submit)
        self.submit_button.pack()

        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

    def _start_recording(self):
        self.transcribed_text_display.delete("1.0", "end")
        self.voice_data = []

        def callback(indata, frames, time, status):
            self.voice_data.append(indata.copy())

        now = datetime.now()
        exact_time = now.strftime("%H-%M-%S") + '_' + now.strftime("%f")[:3]

        self.base_filename = os.path.join("/Users/michaelcunningham/Desktop/Coding/t2tc/temp_recordings", f"{exact_time}")
        self.wav_filename = self.base_filename + ".wav"

        self.stream = sd.InputStream(callback=callback, channels=1, samplerate=self.fs)
        self.stream.start()

    def _stop_recording(self):
        self.stream.stop()
        self.stream.close()
        self.voice_data = np.concatenate(self.voice_data, axis=0)
        write(self.wav_filename, self.fs, self.voice_data)

        self.transcript = self._transcribe()

        self.transcribed_text_display.insert(tk.END, self.transcript)

    def _toggle_recording(self):
        if self.recording:
            self._stop_recording()
            self.record_button.config(text="Re-record")
            self.submit_button.config(state="active")
        else:
            self._start_recording()
            self.record_button.config(text="Stop recording")
            self.submit_button.config(state="disabled")

        self.recording = not self.recording

    def _transcribe(self):
        self.mp3_filename = self.base_filename + ".mp3"
        AudioSegment.from_wav(self.wav_filename).export(self.mp3_filename, format="mp3")

        os.remove(self.wav_filename)

        mp3_file = open(self.mp3_filename, "rb")

        transcript = self.openai_client.audio.transcriptions.create(
            file=mp3_file,
            model="whisper-1",
            language="en",
            response_format="text"
            )
        
        os.remove(self.mp3_filename)

        return transcript
    
    def _submit(self):
        print(f"Submitted {self.transcript}")
        exit()