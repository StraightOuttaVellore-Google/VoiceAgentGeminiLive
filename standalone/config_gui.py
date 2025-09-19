import asyncio
import numpy as np
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext
import threading

from awaaz_connection import AwaazConnection

class VoiceEqualizer(tk.Canvas):
    def __init__(self, parent, width=200, height=60, bars=10):
        super().__init__(parent, width=width, height=height, bg='black')
        self.bars = bars
        self.bar_width = width // bars
        self.height = height
        self.rectangles = []
        
        # Create bars
        for i in range(bars):
            x = i * self.bar_width
            rect = self.create_rectangle(
                x, height,
                x + self.bar_width - 1, height,
                fill='green'
            )
            self.rectangles.append(rect)
        
        self.is_animating = False

    def update_levels(self, audio_data):
        """Update bars based on actual audio levels"""
        if not self.is_animating:
            return
            
        # Convert bytes to numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        # Split audio into segments for each bar
        segments = np.array_split(audio_np, self.bars)
        
        # Calculate RMS for each segment and normalize
        for i, segment in enumerate(segments):
            rms = np.sqrt(np.mean(segment.astype(float)**2))
            # Normalize to 0-1 range and scale to height
            height = min(int((rms / 32768.0) * self.height * 7), self.height)
            
            # Update bar height
            self.coords(
                self.rectangles[i],
                i * self.bar_width, self.height - height,
                (i + 1) * self.bar_width - 1, self.height
            )

    def start_animation(self):
        self.is_animating = True

    def stop_animation(self):
        self.is_animating = False
        # Reset all bars
        for rect in self.rectangles:
            self.coords(rect, 
                self.coords(rect)[0], self.height,
                self.coords(rect)[2], self.height
            )

class ConfigGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sahay ✨")
        self.root.geometry("600x500")
        self.awaaz_client = None
        self.awaaz_thread = None
        self.running = False
        self.cleanup_event = threading.Event()
        self.awaaz_connected = False

        # System Prompt
        tk.Label(self.root, text="System Prompt").pack(pady=5)
        self.system_prompt = scrolledtext.ScrolledText(self.root, width=60, height=10)
        self.system_prompt.pack(pady=5)
        self.system_prompt.insert(tk.END, "You are Awaaz, an empathetic AI mentor. Your goal is to provide a safe space for users to talk about their feelings. Use a supportive and gentle tone. You are multilingual and can converse in English and Hindi.")

        # Voice Selection
        tk.Label(self.root, text="Voice").pack(pady=5)
        self.voice_var = tk.StringVar(value="Puck")
        voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]
        self.voice_dropdown = ttk.Combobox(self.root, textvariable=self.voice_var, values=voices, state="readonly")
        self.voice_dropdown.pack(pady=5)

        # Google Search Checkbox
        self.google_search_var = tk.BooleanVar(value=True)
        self.google_search_cb = tk.Checkbutton(self.root, text="Enable Google Search", variable=self.google_search_var)
        self.google_search_cb.pack(pady=5)

        # Allow Interruptions Checkbox
        self.allow_interruptions_var = tk.BooleanVar(value=False)
        self.interruptions_cb = tk.Checkbutton(
            self.root, 
            text="Allow Interruptions", 
            variable=self.allow_interruptions_var
        )
        self.interruptions_cb.pack(pady=5)

        # Control buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        # Start/Stop buttons
        self.start_button = tk.Button(button_frame, text="Start Awaaz", command=self.start_awaaz)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="Stop Awaaz", command=self.stop_awaaz, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.equalizer = VoiceEqualizer(self.root)
        self.equalizer.pack(pady=20)


    def set_config_state(self, state):
        """Enable or disable all configuration widgets"""
        self.system_prompt.config(state=state)
        self.voice_dropdown.config(state="readonly" if state == "normal" else "disabled")
        self.google_search_cb.config(state=state)
        self.interruptions_cb.config(state=state)

    def get_config(self):
        return {
            "system_prompt": self.system_prompt.get("1.0", tk.END).strip(),
            "voice": self.voice_var.get(),
            "google_search": self.google_search_var.get(),
            "allow_interruptions": self.allow_interruptions_var.get()
        }

    def start_awaaz(self):
        if self.awaaz_thread and self.awaaz_thread.is_alive():
            return

        self.running = True
        config = self.get_config()
        self.awaaz_client = AwaazConnection(
            config, 
            self.cleanup_event,
            on_connect=self.on_awaaz_connected
        )
        self.awaaz_client.set_equalizer(self.equalizer)
        
        self.awaaz_thread = threading.Thread(target=self._run_awaaz_async)
        self.awaaz_thread.start()

        # Only disable the start button initially
        self.start_button.config(state=tk.DISABLED)

    def on_awaaz_connected(self):
        """Called when Awaaz connection is established"""
        self.awaaz_connected = True
        # Now disable configuration and enable stop button
        self.set_config_state("disabled")
        self.stop_button.config(state=tk.NORMAL)
        self.equalizer.start_animation()

    def stop_awaaz(self):
        if not self.running:
            return

        self.running = False
        self.awaaz_connected = False
        if self.awaaz_client:
            self.cleanup_event.set()
            if self.awaaz_thread:
                self.awaaz_thread.join()
            self.awaaz_client = None
            self.cleanup_event.clear()

        self.equalizer.stop_animation()

        # Re-enable configuration after stopping
        self.set_config_state("normal")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def _run_awaaz_async(self):
        try:
            asyncio.run(self.awaaz_client.start())
        except Exception as e:
            print(f"Awaaz error: {e}")
        finally:
            if self.running:
                self.root.after(0, self.stop_awaaz)

    def run(self):
        self.root.mainloop()