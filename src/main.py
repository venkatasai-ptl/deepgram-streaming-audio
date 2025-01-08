import asyncio
from deepgram import Deepgram
import websockets
import pyaudio

# Your Deepgram API key
DEEPGRAM_API_KEY = '916d021522ce7663133b4387d7b6cd37f367fb67'

async def main():
    # Initialize the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)

    # Define the transcription options
    options = {
        "punctuate": True,
        "model": "nova",
        "language": "en-IN"
    }

    # Function to handle received transcriptions
    async def handle_transcription(response):
        if response.get("channel") and response["channel"].get("alternatives"):
            transcript = response["channel"]["alternatives"][0].get("transcript", "")
            if transcript:
                print(f"Transcript: {transcript}")

    # Open microphone audio stream
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024
    )

    try:
        # Connect to Deepgram's live transcription WebSocket API
        async with websockets.connect(
            "wss://api.deepgram.com/v1/listen",
            extra_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
        ) as ws:
            print("Connected to Deepgram. Speak into your microphone.")
            while True:
                # Read audio data from the microphone
                audio_data = stream.read(1024, exception_on_overflow=False)
                # Send audio data to Deepgram
                await ws.send(audio_data)

                # Receive and handle transcription responses
                response = await ws.recv()
                await handle_transcription(response)

    except KeyboardInterrupt:
        print("Stopping transcription.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    asyncio.run(main())
