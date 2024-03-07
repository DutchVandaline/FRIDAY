import pygame
import threading
from auto_delete_audio import delete_old_files
from datetime import datetime
from colorama import Fore


class FridayVoice:
    def __init__(self, output_audio):
        self.output_audio = output_audio
        self.stopped = threading.Event()
        self.finished_playing = False

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.output_audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Adjust the tick rate as needed
        self.finished_playing = True
        print("Voice player finished playing.")

    def wait_for_input(self):
        try:
            input()
        except EOFError:
            pass
    
    def stop(self):
        pygame.mixer.music.stop()
        self.stopped.set()

    def start(self):
        music_thread = threading.Thread(target=self.play_music)
        input_thread = threading.Thread(target=self.wait_for_input)

        music_thread.start()
        input_thread.start()

    def speak_response(response, client):
        print(Fore.YELLOW + "Response GPT-4")
        print(Fore.YELLOW + response)
        tts_response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=response,
                )

        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"Output_Audio/output_{current_time}.mp3"
        tts_response.stream_to_file(output_file)

        voice_player = FridayVoice(output_file)
        voice_player.start()
    

        # Wait until voice_player finishes playing the audio
        while not voice_player.finished_playing:
            pass

        delete_old_files("Output_Audio", 5)
