#!/usr/bin/env python3
"""
Mic Test - Listen through the PS Eye microphone via your headset.
Captures from PS Eye mic, boosts the gain, plays through USB headset.

Press Ctrl+C to stop.
"""

import sounddevice as sd
import numpy as np
import sys

from jetcam import Microphone


def main():
    # Find PS Eye mic
    mic_dev = None
    for d in Microphone.list_devices():
        if "USB Camera" in d["name"]:
            mic_dev = d["index"]
            print(f"Input:  [{d['index']}] {d['name']}")
            break

    if mic_dev is None:
        print("PS Eye mic not found!")
        sys.exit(1)

    # Find USB headset output
    out_dev = None
    for i, d in enumerate(sd.query_devices()):
        if d["max_output_channels"] > 0 and "Headset" in d["name"]:
            out_dev = i
            print(f"Output: [{i}] {d['name']}")
            break

    if out_dev is None:
        print("USB headset not found, using default output")

    samplerate = 16000
    gain = 20.0  # PS Eye is quiet, boost it

    print(f"\nGain: {gain}x")
    print("Listening... speak near the PS Eye camera. Ctrl+C to stop.\n")

    def callback(indata, outdata, frames, time_info, status):
        if status:
            print(f"  {status}")
        # Take channel 0 from PS Eye, boost, send to both headset channels
        mono = indata[:, 0] * gain
        mono = np.clip(mono, -1.0, 1.0)
        outdata[:, 0] = mono
        outdata[:, 1] = mono

    try:
        with sd.Stream(
            device=(mic_dev, out_dev),
            samplerate=samplerate,
            blocksize=512,
            dtype="float32",
            channels=(1, 2),
            callback=callback,
        ):
            print("Audio passthrough active. Press Ctrl+C to stop.")
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
