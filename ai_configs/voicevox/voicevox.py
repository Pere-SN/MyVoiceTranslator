import urllib.parse
import requests
import winsound
import os
API_URL = "http://localhost:50020"


def speak(sentence, speaker_id='20', speed='1', pitch=0, intonation=2, volume=3, prephoneme=1, postphoneme=1):

    params_encoded = urllib.parse.urlencode({'text': sentence, 'speaker': speaker_id})

    r = requests.post(f'{API_URL}/audio_query?{params_encoded}')
    voicevox_query = r.json()
    voicevox_query['speedScale'] = speed
    voicevox_query['pitchScale'] = pitch
    voicevox_query['intonationScale'] = intonation
    voicevox_query['volumeScale'] = volume
    voicevox_query['prePhonemeLength'] = prephoneme
    voicevox_query['postPhonemeLength'] = postphoneme
    voicevox_query['outputSamplingRate'] = 24000

    params_encoded = urllib.parse.urlencode({'speaker': speaker_id, 'enable_interrogative_upspeak': True})
    r = requests.post(f'{API_URL}/synthesis?{params_encoded}', json=voicevox_query)

    speech_filename = '../../audio_files/output_audio.wav'
    os.makedirs(os.path.dirname(speech_filename), exist_ok=True)
    with open(speech_filename, 'wb') as outfile:
        outfile.write(r.content)
    winsound.PlaySound(speech_filename, winsound.SND_FILENAME)


def get_speaker_list():
    url = f'{API_URL}/speakers'
    r = requests.get(url)
    formatted_data = []

    for entry in r.json():
        speaker_name = entry["name"]
        styles = entry["styles"]
        style_dict = {}

        for style in styles:
            style_name = style["name"]
            style_id = style["id"]
            style_dict[style_name] = style_id

        formatted_data.append({speaker_name: style_dict})

    return formatted_data

