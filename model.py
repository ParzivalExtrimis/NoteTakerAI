import audioop
import base64
import datetime
import os
from pathlib import Path
import tempfile
import wave
import openai
from openai import OpenAI
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import pyautogui
from faster_whisper import WhisperModel
import shutil

# ANSI escape codes for colors

# !!!!!! environment variable KMP_DUPLICATE_LIB_OK has been set ( Unsafe ) to bypass multiple OpenMP runtime instance warning. Set in environment variables section of PC. Check validity later

PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

openai.api_key = "sk-proj-9dd8fBkmKQtiwXXPvkbtT3BlbkFJRjglKE0ZQZmCJ0Tovvk1"
client = OpenAI(api_key=openai.api_key)

def gpt_handle(query : str) -> str:
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages = [
            {
                'role' : 'system',
                'content' : 'You are an expert at condensing text into concise and coherent notes'
            },
            {
                'role' : 'user',
                'content' : query
            }
        ],
        temperature = 0.4,
        max_tokens = 500,
        top_p = 1,
        presence_penalty = 0,
        frequency_penalty = 0
    )
    return response.choices[0].message.content.strip()

def encode_image_to_base64(image_path : str):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def analyze_image(image_path: str, user_input: str) -> str:
    base64_image = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages = [
            {
                'role' : 'user',
                'content' : [
                    {
                        'type' : 'text',
                        'text' : f'Get only text from the image along with descriptions of any important diagrams along with a line about the context of the image like location, URL, title etc. \nIf you see a terminal on the screen and the user has not explicitly specified that you also consider the terminal here in this query: {user_input}, then begin your response with YES/NO to indicate as such. Also make sure to ignore the terminal area on the screen if it exists unless the user specifies otherwise here in the query: {user_input}'
                    },
                    {
                        'type' : 'image_url',
                        'image_url' : {
                            'url' : f'data:image/jpeg;base64,{base64_image}',
                        },
                    },
                ],
            },
        ],
        max_tokens = 1000
    )
    return response.choices[0].message.content.strip()

def take_screenshot(filepath: str) -> None:
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)

def tts(text : str) -> None:
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete = False) as tmpfile:
        speech_file_path = tmpfile.name

    response = openai.audio.speech.create(
        model='tts-1',
        voice='shimmer',
        input=text,
        response_format='mp3'
    )

    with open(speech_file_path, 'wb') as f:
        f.write(response.content)

    audio = AudioSegment.from_mp3(speech_file_path)
    play(audio)

    Path(speech_file_path).unlink()


# transcription with whisper
model_size = 'medium.en'
whisper_model = WhisperModel(model_size, device='cuda', compute_type='float16')

def transcribe(audio_file) -> str:
    segments, info = whisper_model.transcribe(audio_file, beam_size=5)
    transcription = ""
    for segment in segments:
        transcription += segment.text + " "
    return transcription.strip()

#record audio
def record_audio(file_path : str, silence_treshold=1000, speech_treshold=1000, chunk_size=1024, format=pyaudio.paInt16, channels=1, rate=16000):
    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)
    frames = []
    silence_count = 0
    silence_frames = int( rate / chunk_size * 2.0 ) # 2 seconds of silence
    speech_frames = int ( rate / chunk_size * 0.3) # 0.3 seconds of speech

    print("Audio capture ready")
    while True:
        data = stream.read(chunk_size)
        rms = audioop.rms(data, 2)

        if rms > speech_treshold:
            print('Recording...')
            break
    
    frames.append(data)

    while True:
        data = stream.read(chunk_size)
        frames.append(data)

        rms = audioop.rms(data, 2)
        if rms < silence_treshold:
            silence_count += 1
            if silence_count > silence_frames:
                break
        else:
            silence_count = 0

    print('Stopping audio capture')

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format=format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()