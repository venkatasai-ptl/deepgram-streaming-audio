import asyncio
import websockets
import pyaudio
import json

# Your Deepgram API key
DEEPGRAM_API_KEY = "916d021522ce7663133b4387d7b6cd37f367fb67"

async def main():
    # WebSocket URL for Deepgram's live transcription
    url = "wss://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}"
    }

    # Connect to the WebSocket
    async with websockets.connect(url, extra_headers=headers) as ws:
        # Define transcription options
        options = {
            "punctuate": True,
            "language": "en-IN",
            "model": "nova"
        }
        await ws.send(json.dumps({"options": options}))

        # Open the microphone stream
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        try:
            print("Streaming microphone audio to Deepgram. Press Ctrl+C to stop.")
            while True:
                # Read audio data from the microphone
                audio_data = stream.read(1024, exception_on_overflow=False)
                # Send audio data to Deepgram
                await ws.send(audio_data)

                # Receive transcription responses
                response = await ws.recv()
                transcription = json.loads(response)
                if transcription.get("channel") and transcription["channel"].get("alternatives"):
                    transcript = transcription["channel"]["alternatives"][0].get("transcript", "")
                    if transcript:
                        print(f"Transcript: {transcript}")
        except KeyboardInterrupt:
            print("Stopped transcription.")
        finally:
            # Cleanup microphone stream
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    asyncio.run(main())
