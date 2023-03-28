import urllib.parse
import requests

base_url = "http://localhost:9000"
language = 'es'


def speech_to_text(audio_file):
    file = {'audio_file': (audio_file, open(audio_file, 'rb'), 'audio/wav')}
    params_encoded = urllib.parse.urlencode({"task": "transcribe", "language": language, "audio_files": "txt"})

    url = f"{base_url}/asr?{params_encoded}"

    r = requests.post(url, files=file)

    if r.status_code == 200:
        return r.text.strip()
    else:
        print("Whisper Error:", r.status_code)


# print(speech_to_text('waifuvoice/generated_files/real_voice_audio.wav'))
