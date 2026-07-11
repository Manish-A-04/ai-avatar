import asyncio
from pathlib import Path

# Important: Run this script from the backend directory using your virtual environment
from app.pipeline.tts.service import tts_service
from app.pipeline.lipsync.service import lipsync_service
from app.config import settings

async def main():
    print("=== Pipeline Test Script ===")
    
    print("1. Loading TTS model (Kokoro)...")
    tts_service.load()
    
    print("2. Loading Wav2Lip model...")
    lipsync_service.load()
    
    if lipsync_service._model is None:
        print("\n[ERROR] Wav2Lip model not loaded.")
        print("Did you clone Easy-Wav2Lip into the 'wav2lip' folder and download 'Wav2Lip_GAN.pt' and 's3fd.pth'?")
        print("Please check the instructions in walkthrough.md")
        return
        
    system_avatars_dir = settings.media_dir / "system_avatars"
    system_avatars_dir.mkdir(parents=True, exist_ok=True)
    
    avatar_images = [f for f in system_avatars_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
    
    if not avatar_images:
        print(f"\n[ERROR] No avatar images found in {system_avatars_dir}")
        print("Please paste at least one .png or .jpg image in that folder.")
        return
        
    image_path = str(avatar_images[0])
    print(f"\nAutomatically selected avatar: {image_path}")
        
    test_text = """
    In a world where technology advances at an unprecedented rate, 
    the ability to communicate effectively remains paramount. 
    From the earliest days of the telegraph to the modern era of artificial intelligence, 
    the human voice continues to be our most powerful tool for connection. 
    Whether you are listening to a podcast, navigating a car with GPS, 
    or speaking with a virtual assistant, 
    the quality of the voice synthesis determines the user's experience.

    """
    print(f"\n3. Synthesizing audio for text: '{test_text}'")
    
    audio_dir = settings.media_dir / "audio"
    audio_path = await tts_service.synthesize(
        text=test_text,
        output_dir=audio_dir
    )
    print(f"   ✓ Audio generated at: {audio_path}")
    
    print(f"\n4. Animating avatar...")
    video_dir = settings.media_dir / "videos"
    video_path = await lipsync_service.animate(
        image_path=image_path,
        audio_path=audio_path,
        output_dir=video_dir
    )
    
    if video_path:
        print(f"\n[SUCCESS] Video generated successfully at: {video_path}")
    else:
        print("\n[ERROR] Failed to generate video. Check the logs for Out of Memory or face detection errors.")

if __name__ == "__main__":
    # Ensure media directories exist
    (settings.media_dir / "audio").mkdir(parents=True, exist_ok=True)
    (settings.media_dir / "videos").mkdir(parents=True, exist_ok=True)
    
    asyncio.run(main())
