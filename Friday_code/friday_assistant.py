import openai
import time
from datetime import datetime

from friday_voice import FridayVoice
from friday_whisper import FridayListen
from auto_delete_audio import delete_old_files

client = openai.Client(api_key="Your_API_KEY")

while True:
    inputMessage = str(FridayListen.transcribe_regular_speech())
    

    message = client.beta.threads.messages.create(
        thread_id="Your_THREAD_KEY",
        role="user",
        content=inputMessage,
    )

    run = client.beta.threads.runs.create(
        thread_id="Your_THREAD_KEY",
        assistant_id="Your_ASSISTANT_KEY",
        instructions="You are a assistant who is similar to J.A.R.V.I.S and F.R.I.D.A.Y from movie \"Ironman\""
    )

    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id="Your_THREAD_KEY",
                                                       run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            print("Run failed:", run_status.last_error)
            break
        time.sleep(2)

    messages = client.beta.threads.messages.list(
        thread_id="Your_THREAD_KEY"
    )

    print(messages)

    last_message = messages.data[0]
    response_text = last_message.content[0].text.value
    print(f'Last Response: {response_text}')

    tts_response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=response_text,
    )

    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"Output_Audio/output_{current_time}.mp3"
    tts_response.stream_to_file(output_file)

    voice_player = FridayVoice(output_file)
    voice_player.start()

    delete_old_files("Output_Audio", 5)

    user_input = input("Press Enter to continue or type 'exit' to quit: ")
    voice_player.stop()
    if user_input.lower() == "exit":
        break
