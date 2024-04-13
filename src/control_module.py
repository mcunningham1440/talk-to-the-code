import tkinter as tk
import sounddevice as sd
import numpy as np
from openai import OpenAI
from datetime import datetime
import json

from config import *
from src.ctrl_module_utils import *
from src.code_agent_utils import *


class ControlModule:
    def __init__(self, root, code_dir):
        self.root = root

        self.recording = False

        self.label = tk.Label(root, text="Transcribed_text")

        self.transcribed_text_display = tk.Text(root)
        self.transcribed_text_display.pack()

        self.record_button = tk.Button(root, text="Record", command=self._toggle_recording)
        self.record_button.pack()

        self.submit_button = tk.Button(root, text="Submit", state='disabled', command=self._submit)
        self.submit_button.pack()

        self.openai_client = OpenAI()
        self.code_dir = code_dir


    def _start_recording(self):
        self.transcribed_text_display.delete("1.0", "end")
        self.voice_data = []

        def callback(indata, frames, time, status):
            self.voice_data.append(indata.copy())

        self.stream = sd.InputStream(
            callback=callback,
            channels=1, 
            samplerate=config.sampling_freq
            )
        self.stream.start()


    def _stop_recording(self):
        self.stream.stop()
        self.stream.close()
        self.voice_data = np.concatenate(self.voice_data, axis=0)

        now = datetime.now()
        self.recording_time = now.strftime("%H-%M-%S") + '_' + now.strftime("%f")[:3]

        self.transcript = get_voice_transcript(
            self.voice_data, 
            self.openai_client,
            self.recording_time
            )

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

    
    def _submit(self):
        self.chat_history = generate_agent_response(
            self.transcript, 
            self.code_dir
            )
        if self.chat_history.chat_history[-1]['content'] == "TERMINATE":
            final_answer = self.chat_history.chat_history[-2]['content']
        else:
            final_answer = self.chat_history.chat_history[-1]['content']

        string_subs = [
            ("\n", ""),
            ("`", ""),
            ("TERMINATE", "")
        ]
        for sub in string_subs:
            final_answer = final_answer.replace(*sub)

        print("Got here")

        if config.speech_output_mode == "openai":
            speech_log_name = f"{self.recording_time}.mp3"
            speech_log_path = os.path.join("speech_logs", speech_log_name)

            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=final_answer
                )
            
            response.stream_to_file(speech_log_path)

            os.system(f"afplay {speech_log_path}")
        else:
            print("Got further")
            os.system(f"""say 
                      "{final_answer}"
                      """)
        
        agent_log_name = f"{self.recording_time}.json"
        with open(os.path.join("agent_logs", agent_log_name), "w") as file:
            json.dump(self.chat_history, file)