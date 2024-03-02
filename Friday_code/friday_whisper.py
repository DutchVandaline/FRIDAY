from faster_whisper import WhisperModel
import speech_recognition as sr

model_size = "tiny"
model = WhisperModel(model_size, device="cpu", compute_type="int8")



class FridayListen:
    def transcribe_whisper_audio(audio_file):
        segments, info = model.transcribe(audio_file, beam_size=5)

        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))


    def transcribe_regular_speech():
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Listening...")

            recognizer.adjust_for_ambient_noise(source)

            audio = recognizer.listen(source)

        try:
            print("Transcribing...")
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            print("Sorry, I couldn't request results from Google Speech Recognition service; {0}".format(e))