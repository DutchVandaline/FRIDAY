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

            #Check if the word "Friday" is present in the recognized text
            # if "Friday" in text:
            #     # Extract the text after "Friday"
            #     index = text.index("Friday") + len("Friday")
            #     text_after_friday = text[index:].strip()
            #     print(text_after_friday)
            #     return text_after_friday
            # else:
            #     return None

        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return None
        except sr.RequestError as e:
            print("Sorry, I couldn't request results from Google Speech Recognition service; {0}".format(e))
            return None

    def listen_for_hotword():
        recognizer = sr.Recognizer()

        while True:
            with sr.Microphone() as source:
                print("Waiting for hotword...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                hotword = recognizer.recognize_google(audio).lower()
                if "friday" in hotword:
                    print("Hotword 'Friday' detected! Proceeding with further instructions...")
                    return True
                else:
                    return False
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service; check your internet connection")
