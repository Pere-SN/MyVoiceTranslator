import pyaudio
import wave
from pydb import AudioSegment
import tempfile


def show_available_input_devices():
    p = pyaudio.PyAudio()

    print("Available input devices:")
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if dev_info['maxInputChannels'] > 0:
            print(f"{i}: {dev_info['name']}")

    while True:
        try:
            selected_device_index = int(input("Select an input device by index: "))
            dev_info = p.get_device_info_by_index(selected_device_index)
            if dev_info['maxInputChannels'] > 0:
                break
        except:
            pass
        print("Invalid selection, please try again.")

    p.terminate()

    return selected_device_index


def send_audio_to_virtual_microphone(device_index, file_path):
    chunk = 2048
    a_format = pyaudio.paInt16
    a_channels = 1
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(42000)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio.export(format="wav").read())

    p = pyaudio.PyAudio()

    stream = p.open(format=a_format,
                    channels=a_channels,
                    rate=42000,
                    output=True,
                    input_device_index=device_index)

    wf = wave.open(tmp.name, 'rb')

    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    stream.close()



# Example usage:
# selected_device_index = show_available_input_devices()
# send_audio_to_virtual_microphone(2, '../generated_files/audio_files.wav')
