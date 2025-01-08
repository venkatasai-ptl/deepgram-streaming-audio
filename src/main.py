from deepgram import Deepgram
import pyaudio
import asyncio

# Your Deepgram API Key
DEEPGRAM_API_KEY = '916d021522ce7663133b4387d7b6cd37f367fb67'

async def main():
    # Initialize the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)

    # Define the transcription handler
    async def process_transcription(transcription):
        if transcription.get('channel') and transcription['channel'].get('alternatives'):
            transcript = transcription['channel']['alternatives'][0].get('transcript', '')
            if transcript:
                print(f"Transcript: {transcript}")

    # Start the WebSocket connection
    options = {
        "punctuate": True,
        "model": "nova",
        "language": "en-IN"
    }

    # Open microphone stream
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024
    )

    async with deepgram.transcription.live(process_transcription, options=options) as dg_socket:
        print("Microphone streaming to Deepgram. Press Ctrl+C to stop.")
        try:
            while True:
                data = stream.read(1024, exception_on_overflow=False)
                await dg_socket.send(data)
        except KeyboardInterrupt:
            print("Stopped by user.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    asyncio.run(main())
