import asyncio
import traceback
import websockets.exceptions
from .config import Config
from .audio import AudioManager
from .video import VideoManager
from .session import SessionManager

class LiveClient:
    """Main client that orchestrates all components of the Gemini Live API"""
    
    def __init__(self, video_mode=Config.DEFAULT_VIDEO_MODE):
        self.video_mode = video_mode
        
        # Initialize managers
        self.audio_manager = AudioManager()
        self.video_manager = VideoManager(video_mode)
        self.session_manager = SessionManager()
        
        # Queues
        self.audio_in_queue = None
        self.out_queue = None
        
    async def send_text(self):
        """Handle text input from user"""
        print("\n=== Gemini Live API Started ===")
        print("Commands:")
        print("- Type your message and press Enter")
        print("- 'q' or 'quit' to exit")
        print("- 'camera on/off' to toggle camera")
        print("- 'screen on/off' to toggle screen sharing")
        print("- 'status' to check current settings\n")

        while True:
            try:
                text = await asyncio.to_thread(input, "message > ")

                if text.lower() in ["q", "quit"]:
                    break
                elif text.lower() == "camera off":
                    self.video_manager.toggle_camera(False)
                    print("📷 Camera disabled")
                    continue
                elif text.lower() == "camera on":
                    self.video_manager.toggle_camera(True)
                    print("📷 Camera enabled")
                    continue
                elif text.lower() == "screen off":
                    self.video_manager.toggle_screen(False)
                    print("🖥️ Screen sharing disabled")
                    continue
                elif text.lower() == "screen on":
                    self.video_manager.toggle_screen(True)
                    print("🖥️ Screen sharing enabled")
                    continue
                elif text.lower() == "status":
                    print(f"📊 Status:")
                    print(f"  Mode: {self.video_mode}")
                    print(f"  Camera: {'✅ enabled' if self.video_manager.camera_enabled else '❌ disabled'}")
                    print(f"  Screen: {'✅ enabled' if self.video_manager.screen_enabled else '❌ disabled'}")
                    continue

                if text.strip():
                    await self.session_manager.session.send(input=text or ".", end_of_turn=True)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error in send_text: {e}")

    async def run(self):
        """Main execution loop"""
        print(f"\n🚀 Starting Gemini Live API")
        print(f"📱 Mode: {self.video_mode}")
        print(f"🔑 API Key: {'✅ Loaded' if Config.GEMINI_API_KEY else '❌ Missing'}")
        print(f"🤖 Model: {Config.MODEL_NAME}")

        try:
            # Get the connection context manager
            connection_manager = await self.session_manager.try_connect_with_fallbacks()
            
            async with (
                connection_manager as session,
                asyncio.TaskGroup() as tg,
            ):
                print("✅ Connected to Gemini Live API successfully!")

                # Initialize queues
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                # Setup managers
                await self.session_manager.setup_session(session, self.audio_in_queue)
                await self.audio_manager.setup_audio_queues(self.audio_in_queue, self.out_queue)
                await self.video_manager.setup_video_queue(self.out_queue)

                # Create tasks
                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.session_manager.send_realtime(self.out_queue))
                tg.create_task(self.audio_manager.listen_audio())

                # Video tasks based on mode
                if self.video_mode == "camera":
                    tg.create_task(self.video_manager.get_frames())
                elif self.video_mode == "screen":
                    tg.create_task(self.video_manager.get_screen())
                elif self.video_mode == "both":
                    tg.create_task(self.video_manager.get_frames())
                    tg.create_task(self.video_manager.get_screen())

                tg.create_task(self.session_manager.receive_audio())
                tg.create_task(self.audio_manager.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            print("👋 Exiting...")
        except websockets.exceptions.ConnectionClosedError as e:
            if "quota" in str(e).lower() or "1011" in str(e):
                print("🚨 QUOTA EXCEEDED ERROR")
                print(Config.get_quota_error_message())
                print("\n💡 Quick fixes:")
                print("\n1. Wait a few hours for quota reset")
                print("2. Try a different API key")
                print("3. Check your billing at https://aistudio.google.com/")
            else:
                print(f"❌ Connection error: {e}")
        except Exception as e:
            if "quota" in str(e).lower():
                print("🚨 QUOTA EXCEEDED ERROR")
                print(Config.get_quota_error_message())
            elif "All models" in str(e) or "All available models" in str(e):
                pass  # Error message already printed
            else:
                print(f"❌ Unexpected error: {e}")
                traceback.print_exc()
        finally:
            self.cleanup()
            print("🛑 Application terminated\n")

    def cleanup(self):
        """Clean up all resources"""
        try:
            self.audio_manager.cleanup()
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
