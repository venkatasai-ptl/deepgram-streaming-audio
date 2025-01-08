from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions
import pyaudio
import threading

# The API key you created in step 1
DEEPGRAM_API_KEY = '5068995718d38dbe230909ce1a989e3365dd8804'

def main():
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        dg_connection = deepgram.listen.live.v('1')

        # Listen for any transcripts received from Deepgram and write them to the console
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            print(f'transcript: {sentence}')

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        # Create a websocket connection to Deepgram
        options = LiveOptions(
            smart_format=True, model="nova-2", language="en-IN"
        )
        dg_connection.start(options)

        lock_exit = threading.Lock()
        exit = False

        # Listen for the connection to open and send streaming audio from the microphone to Deepgram
        def myThread():
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,  # 16-bit audio format
                channels=1,  # Mono audio
                rate=16000,  # Sampling rate
                input=True,  # Specify that this is an input stream
                frames_per_buffer=1024  # Size of each audio chunk
            )

            try:
                while True:
                    audio_data = stream.read(1024, exception_on_overflow=False)
                    lock_exit.acquire()
                    if exit:
                        break
                    lock_exit.release()

                    dg_connection.send(audio_data)
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()

        myMic = threading.Thread(target=myThread)
        myMic.start()

        input('Press Enter to stop transcription...\n')
        lock_exit.acquire()
        exit = True
        lock_exit.release()

        myMic.join()

        # Indicate that we've finished by sending the close stream message
        dg_connection.finish()
        print('Finished')

    except Exception as e:
        print(f'Could not open socket: {e}')
        return

if __name__ == '__main__':
    main()
