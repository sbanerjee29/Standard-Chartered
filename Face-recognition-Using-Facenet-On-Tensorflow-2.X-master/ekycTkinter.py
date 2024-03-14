import os
import tkinter as tk
import cv2
import sounddevice as sd
import numpy as np
import threading
import wave
import ffmpeg
import time
import webbrowser

class KYCApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("KYC Solution")

        self.start_button = tk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_button.pack()

        self.stop_button = tk.Button(self.root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack()

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        self.video_capture = None
        self.audio_thread = None
        self.output_path = None
        self.is_recording = False

    def start_recording(self):
        self.video_capture = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        frame_width = int(self.video_capture.get(3))
        frame_height = int(self.video_capture.get(4))
        timestamp = int(time.time())
        video_filename = f"recorded_cam_{timestamp}.avi"
        audio_filename = f"recorded_audio_{timestamp}.wav"
        self.output_path = os.path.join(os.getcwd(), 'Video', video_filename)
        audio_output_path = os.path.join(os.getcwd(), 'Video', audio_filename)
        out = cv2.VideoWriter(self.output_path, fourcc, 20.0, (frame_width, frame_height))

        self.is_recording = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start audio recording in a separate thread
        self.audio_thread = threading.Thread(target=self.record_audio, args=(audio_output_path,))
        self.audio_thread.start()

        while self.is_recording:
            ret, frame = self.video_capture.read()
            if ret:
                out.write(frame)
                cv2.imshow('Recording', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break

        out.release()
        self.video_capture.release()
        cv2.destroyAllWindows()

    def record_audio(self, output_path):
        samplerate = 44100
        duration = 10  # seconds
        channels = 2

        frames = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=channels, blocking=True)

        wf = wave.open(output_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit encoding
        wf.setframerate(samplerate)
        wf.writeframes(frames.tobytes())
        wf.close()

    def stop_recording(self):
        self.is_recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        if self.output_path:
            self.audio_thread.join()  # Wait for the audio recording thread to finish

            # Convert video to MP4
            self.convert_to_mp4(self.output_path)

    def convert_to_mp4(self, file_path):
        output_path = os.path.splitext(file_path)[0] + '.mp4'
        ffmpeg.input(file_path).output(output_path).run(overwrite_output=True)

        # Remove the original file
        os.remove(file_path)

        # Open the browser window automatically
        webbrowser.open('http://localhost:5000')

if __name__ == "__main__":
    video_folder = os.path.join(os.getcwd(), 'Video')
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)

    root = tk.Tk()
    app = KYCApplication(root)
    root.mainloop()
