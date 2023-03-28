import keyboard
import pyaudio
import wave
import os


def record_audio(key):
    audio_format = pyaudio.paInt16
    audio_channels = 1
    audio_rate = 44100
    audio_chunk = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=audio_format,
                        channels=audio_channels,
                        rate=audio_rate,
                        input=True,
                        frames_per_buffer=audio_chunk)

    frames = []

    while keyboard.is_pressed(key):
        data = stream.read(audio_chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    return frames, audio_rate, audio_channels, audio_format


def save_audio(frames, rate, channels, audio_format, filename="output.wav"):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(audio_format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    return os.path.abspath(filename)


def record_and_save_audio(key, filename="output.wav"):
    while True:
        keyboard.wait(key)
        frames, rate, channels, audio_format = record_audio(key)
        file_path = save_audio(frames, rate, channels, audio_format, filename)
        if not keyboard.is_pressed(key):
            break
