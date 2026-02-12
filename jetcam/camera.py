"""
Camera module - handles video capture from USB cameras.
Designed to work with any V4L2-compatible USB camera.
"""

import cv2
import threading
import time


class Camera:
    """Threaded USB camera capture with clean start/stop lifecycle."""

    def __init__(self, device=0, width=640, height=480, fps=30):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps

        self._cap = None
        self._frame = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    @property
    def is_running(self):
        return self._running

    @property
    def frame(self):
        """Get the latest frame (thread-safe). Returns None if no frame yet."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def start(self):
        """Open the camera and begin capturing frames in a background thread."""
        if self._running:
            return self

        self._cap = cv2.VideoCapture(self.device, cv2.CAP_V4L2)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera device {self.device}")

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._cap.set(cv2.CAP_PROP_FPS, self.fps)

        # Read actual values (camera may not support requested settings)
        actual_w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self._cap.get(cv2.CAP_PROP_FPS)
        print(f"Camera opened: {actual_w}x{actual_h} @ {actual_fps:.1f}fps on /dev/video{self.device}")

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        return self

    def stop(self):
        """Stop capturing and release the camera."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=3)
            self._thread = None
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def _capture_loop(self):
        """Background thread: continuously grabs frames."""
        while self._running:
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame
            else:
                time.sleep(0.001)

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()

    @staticmethod
    def list_devices():
        """Probe /dev/video* and return list of working device indices."""
        import glob
        devices = []
        for path in sorted(glob.glob("/dev/video*")):
            idx = int(path.replace("/dev/video", ""))
            cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    devices.append({"index": idx, "path": path, "resolution": f"{w}x{h}"})
                cap.release()
        return devices
