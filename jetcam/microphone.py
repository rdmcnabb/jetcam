"""
Microphone module - handles audio capture from USB cameras/mics.
Designed to work with any ALSA-compatible USB audio device.
"""

import sounddevice as sd
import numpy as np
import threading
import queue


class Microphone:
    """Threaded USB microphone capture with level monitoring."""

    def __init__(self, device=None, samplerate=16000, channels=1, blocksize=1024):
        self.device = device
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize

        self._stream = None
        self._running = False
        self._level = 0.0
        self._lock = threading.Lock()
        self._audio_queue = queue.Queue(maxsize=100)

    @property
    def is_running(self):
        return self._running

    @property
    def level(self):
        """Current audio level (RMS, 0.0 to 1.0)."""
        with self._lock:
            return self._level

    def start(self):
        """Open the mic and begin capturing audio."""
        if self._running:
            return self

        device_info = sd.query_devices(self.device, 'input')
        print(f"Microphone opened: {device_info['name']} "
              f"- {self.channels}ch @ {self.samplerate}Hz")

        self._stream = sd.InputStream(
            device=self.device,
            samplerate=self.samplerate,
            channels=self.channels,
            blocksize=self.blocksize,
            dtype='float32',
            callback=self._audio_callback,
        )
        self._running = True
        self._stream.start()
        return self

    def stop(self):
        """Stop capturing and release the mic."""
        self._running = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice for each audio block."""
        if status:
            print(f"Audio: {status}")
        rms = np.sqrt(np.mean(indata ** 2))
        with self._lock:
            self._level = min(float(rms), 1.0)
        # Non-blocking put - drop old audio if consumer is slow
        try:
            self._audio_queue.put_nowait(indata.copy())
        except queue.Full:
            try:
                self._audio_queue.get_nowait()
                self._audio_queue.put_nowait(indata.copy())
            except queue.Empty:
                pass

    def read(self, timeout=0.1):
        """Read the next audio block. Returns numpy array or None."""
        try:
            return self._audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()

    @staticmethod
    def list_devices():
        """List available audio input devices."""
        devices = []
        for i, d in enumerate(sd.query_devices()):
            if d['max_input_channels'] > 0:
                devices.append({
                    "index": i,
                    "name": d['name'],
                    "channels": d['max_input_channels'],
                    "samplerate": d['default_samplerate'],
                })
        return devices
