import asyncio
import base64
import io
import cv2
import PIL.Image
import mss
from ..config import Config

class VideoManager:
    """Manages video capture from camera and screen"""
    
    def __init__(self, video_mode=Config.DEFAULT_VIDEO_MODE):
        self.video_mode = video_mode
        self.camera_enabled = video_mode in ["camera", "both"]
        self.screen_enabled = video_mode in ["screen", "both"]
        self.out_queue = None
        
    async def setup_video_queue(self, out_queue):
        """Initialize video output queue"""
        self.out_queue = out_queue
        
    def toggle_camera(self, enabled):
        """Toggle camera on/off"""
        self.camera_enabled = enabled
        
    def toggle_screen(self, enabled):
        """Toggle screen sharing on/off"""
        self.screen_enabled = enabled
        
    def _get_frame(self, cap):
        """Capture and process camera frame"""
        if not self.camera_enabled:
            return None

        ret, frame = cap.read()
        if not ret:
            return None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)
        img.thumbnail(Config.MAX_IMAGE_SIZE)

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg", quality=Config.IMAGE_QUALITY)
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        """Camera capture loop"""
        cap = await asyncio.to_thread(cv2.VideoCapture, 0)

        try:
            while True:
                if self.camera_enabled:
                    frame = await asyncio.to_thread(self._get_frame, cap)
                    if frame:
                        await self.out_queue.put(frame)

                await asyncio.sleep(Config.CAMERA_CAPTURE_INTERVAL)
        except Exception as e:
            print(f"❌ Error in get_frames: {e}")
        finally:
            cap.release()

    def _get_screen(self):
        """Capture and process screen frame"""
        if not self.screen_enabled:
            return None

        try:
            sct = mss.mss()
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            screenshot = sct.grab(monitor)

            img = PIL.Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.thumbnail(Config.MAX_SCREEN_SIZE, PIL.Image.Resampling.LANCZOS)

            image_io = io.BytesIO()
            img.save(image_io, format="jpeg", quality=Config.SCREEN_QUALITY, optimize=True)
            image_io.seek(0)

            mime_type = "image/jpeg"
            image_bytes = image_io.read()
            return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}
        except Exception as e:
            print(f"❌ Error capturing screen: {e}")
            return None

    async def get_screen(self):
        """Screen capture loop"""
        while True:
            try:
                if self.screen_enabled:
                    frame = await asyncio.to_thread(self._get_screen)
                    if frame:
                        await self.out_queue.put(frame)

                await asyncio.sleep(Config.SCREEN_CAPTURE_INTERVAL)
            except Exception as e:
                print(f"❌ Error in get_screen: {e}")
                await asyncio.sleep(1.0)
