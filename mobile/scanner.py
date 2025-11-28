# scanner.py
import threading
import time

# Try to import cv2 and pyzbar
try:
    import cv2
    from pyzbar import pyzbar
    CV_AVAILABLE = True
except Exception as e:
    CV_AVAILABLE = False

class CameraScanner:
    """
    Simple camera scanner using OpenCV + pyzbar.
    Usage:
        s = CameraScanner(on_code_callback)
        s.start()
        s.stop()
    """
    def __init__(self, on_code, camera_index=0):
        self.on_code = on_code
        self.camera_index = camera_index
        self._running = False
        self._thread = None
        self.last_seen = set()
        self._lock = threading.Lock()

    def start(self):
        if not CV_AVAILABLE:
            raise RuntimeError("OpenCV/pyzbar not available. Install opencv-python and pyzbar.")
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None

    def _loop(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self._running = False
            return
        while self._running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue
            barcodes = pyzbar.decode(frame)
            for b in barcodes:
                code = b.data.decode("utf-8")
                # simple de-dup within short window
                with self._lock:
                    if code in self.last_seen:
                        continue
                    self.last_seen.add(code)
                # callback
                try:
                    self.on_code(code)
                except Exception:
                    pass
            # keep last_seen short
            with self._lock:
                if len(self.last_seen) > 50:
                    self.last_seen.clear()
            time.sleep(0.05)
        cap.release()
