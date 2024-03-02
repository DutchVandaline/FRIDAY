import pygame
import threading

class FridayVoice:
    def __init__(self, output_audio):
        self.output_audio = output_audio
        self.stopped = threading.Event()

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.output_audio)
        pygame.mixer.music.play()

    def wait_for_input(self):
        input()
    
    def stop(self):
        pygame.mixer.music.stop()
        self.stopped.set()

    def start(self):
        music_thread = threading.Thread(target=self.play_music)
        input_thread = threading.Thread(target=self.wait_for_input)

        music_thread.start()
        input_thread.start()
