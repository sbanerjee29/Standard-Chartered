import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import speech_recognition as sr
from openpyxl import Workbook

class SpeechRecognitionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Speech Recognition")
        self.master.geometry("400x300")
        
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12))
        
        self.recognizer = sr.Recognizer()
        self.recognizer_thread = None
        
        self.create_widgets()
        
    def create_widgets(self):
        self.start_button = ttk.Button(self.master, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=10)
        
        self.result_label = ttk.Label(self.master, text="", font=("Helvetica", 14))
        self.result_label.pack(pady=5)
        
        self.status_label = ttk.Label(self.master, text="", font=("Helvetica", 10))
        self.status_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self.master, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
        
    def start_recording(self):
        if self.recognizer_thread and self.recognizer_thread.is_alive():
            messagebox.showinfo("Info", "Recording is already in progress.")
            return
        
        self.result_label.config(text="")
        self.status_label.config(text="Listening...", foreground="white")
        self.progress_bar.pack(pady=5)
        self.progress_bar.start()
        
        self.recognizer_thread = threading.Thread(target=self.recognize_speech)
        self.recognizer_thread.start()
        
    def recognize_speech(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio_data = self.recognizer.listen(source)
                self.status_label.config(text="Recognizing...", foreground="white")
                
                text = self.recognizer.recognize_google(audio_data)
                self.result_label.config(text=text)
                self.status_label.config(text="Recognition Complete", foreground="green")
        except sr.UnknownValueError:
            self.status_label.config(text="Error: Could not understand audio.", foreground="red")
        except sr.RequestError as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")
        finally:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    def save_to_excel(self, text):
        workbook = Workbook()
        sheet = workbook.active
        sheet['A1'] = "Recognized Text"
        sheet['B1'] = text
        
        # Choose filename and save the workbook
        filename = "recognized_text.xlsx"
        workbook.save(filename)
        messagebox.showinfo("Info", f"Recognized text saved to '{filename}'")


def main():
    root = tk.Tk()
    app = SpeechRecognitionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
