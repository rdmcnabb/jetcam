# jetcam

USB camera and microphone library for Linux. Built for NVIDIA Jetson but works on any Linux system.

Includes out-of-tree kernel module build for the **PlayStation Eye** camera on Jetson (Tegra kernel), which doesn't ship with the `gspca_ov534` driver.

## Features

- Threaded video capture from any V4L2 USB camera
- Threaded audio capture from any ALSA USB microphone
- PS Eye 4-microphone array support
- Simple `with` statement API - start/stop handled automatically
- Designed as a building block for computer vision and audio projects

## Install

```bash
git clone https://github.com/rdmcnabb/jetcam.git
cd jetcam
pip install -e .
```

OpenCV is required but not auto-installed (Jetson users typically have it pre-installed):
```bash
pip install opencv-python  # if you don't have it already
```

## Quick Start

```python
from jetcam import Camera, Microphone

# Video capture
with Camera(device=0, width=640, height=480, fps=30) as cam:
    frame = cam.frame  # numpy array (H, W, 3), or None if no frame yet

# Audio capture
with Microphone(device=24, samplerate=16000, channels=1) as mic:
    level = mic.level       # RMS level (float, 0.0 to 1.0)
    audio = mic.read()      # numpy array, or None

# List available devices
Camera.list_devices()
Microphone.list_devices()
```

## PS Eye on Jetson (Tegra Kernel)

The Tegra kernel doesn't include the `gspca_ov534` driver. This repo includes the source and a Makefile to build it:

```bash
# Build the kernel modules (one-time)
cd kernel_module/gspca
make

# Load them (required after each reboot)
sudo bash load_pseye.sh
```

To auto-load on boot:
```bash
sudo cp kernel_module/gspca/gspca_main.ko /lib/modules/$(uname -r)/extra/
sudo cp kernel_module/gspca/gspca_ov534.ko /lib/modules/$(uname -r)/extra/
sudo depmod -a
echo -e "gspca_main\ngspca_ov534" | sudo tee /etc/modules-load.d/pseye.conf
```

## Examples

Run the live video + audio level meter:
```bash
python examples/live_feed.py
```

Controls: `q`/`ESC` quit, `s` screenshot, `f` fullscreen

## Tested On

- NVIDIA Jetson AGX Orin (JetPack 6 / L4T R36.4.7)
- Sony PlayStation Eye (USB, 640x480 @ 30fps, 4-mic array)

## License

MIT
