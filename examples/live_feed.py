#!/usr/bin/env python3
"""
Live Feed - Video + Audio from USB camera.
Shows live video with an audio level meter overlay.

Controls:
  q / ESC  - quit
  s        - save screenshot
  f        - toggle fullscreen
"""

import cv2
import numpy as np
import time
import sys
import os

from jetcam import Camera, Microphone


def draw_audio_meter(frame, level, x=20, y=None, width=200, height=20):
    """Draw an audio level meter on the frame."""
    if y is None:
        y = frame.shape[0] - 40

    # Background bar
    cv2.rectangle(frame, (x, y), (x + width, y + height), (40, 40, 40), -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (100, 100, 100), 1)

    # Level fill - green to yellow to red
    bar_width = int(width * min(level * 5, 1.0))  # scale up for visibility
    if bar_width > 0:
        color = (0, 255, 0) if level < 0.1 else (0, 255, 255) if level < 0.2 else (0, 0, 255)
        cv2.rectangle(frame, (x + 1, y + 1), (x + bar_width, y + height - 1), color, -1)

    # Label
    cv2.putText(frame, "MIC", (x + width + 8, y + height - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)


def draw_info_overlay(frame, fps, cam_info=""):
    """Draw FPS and camera info."""
    h, w = frame.shape[:2]
    text = f"{w}x{h} | {fps:.0f} FPS"
    if cam_info:
        text += f" | {cam_info}"
    cv2.putText(frame, text, (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


def main():
    # Auto-detect PS Eye mic (USB Camera) or fall back to default
    mic_device = None
    for dev in Microphone.list_devices():
        if "USB Camera" in dev["name"]:
            mic_device = dev["index"]
            print(f"Found PS Eye mic: [{dev['index']}] {dev['name']}")
            break

    if mic_device is None:
        print("PS Eye mic not found, using default input")

    # Print available cameras
    print("Scanning cameras...")
    for cam in Camera.list_devices():
        print(f"  [{cam['index']}] {cam['path']} - {cam['resolution']}")

    cam_device = 0
    if len(sys.argv) > 1:
        cam_device = int(sys.argv[1])

    print(f"\nStarting live feed (camera={cam_device})...")
    print("Controls: q/ESC=quit, s=screenshot, f=fullscreen\n")

    window_name = "Live Feed"
    fullscreen = False

    with Camera(device=cam_device, width=640, height=480, fps=30) as cam, \
         Microphone(device=mic_device, samplerate=16000, channels=1) as mic:

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)

        fps_counter = 0
        fps_time = time.time()
        display_fps = 0.0
        screenshot_count = 0

        while True:
            frame = cam.frame
            if frame is None:
                time.sleep(0.01)
                continue

            # FPS calculation
            fps_counter += 1
            now = time.time()
            elapsed = now - fps_time
            if elapsed >= 1.0:
                display_fps = fps_counter / elapsed
                fps_counter = 0
                fps_time = now

            # Draw overlays
            draw_info_overlay(frame, display_fps)
            draw_audio_meter(frame, mic.level)

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):  # q or ESC
                break
            elif key == ord('s'):
                screenshot_count += 1
                fname = f"screenshot_{screenshot_count:03d}.png"
                cv2.imwrite(fname, frame)
                print(f"Saved {fname}")
            elif key == ord('f'):
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                                          cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                                          cv2.WINDOW_NORMAL)

    cv2.destroyAllWindows()
    print("Live feed stopped.")


if __name__ == "__main__":
    main()
