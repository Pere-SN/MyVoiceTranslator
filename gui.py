import customtkinter
import threading
from ai_configs.whisper.whisper import speech_to_text
import audio_configs.audio_recording as input_audio
import ai_configs.libretranslate.libretranslate as libre
import ai_configs.voicevox.voicevox as voiceb
import tkinter as tk
import tkinter.ttk as ttk
import time
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class Gui(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Eet window properties
        self.title("MVT - My Voice Translator")
        self.geometry("900x500")
        self.resizable(width=False, height=False)

        # Configure grid layout (2x4)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure((1, 2), weight=1)
        self.languages = libre.get_language()
        self.speakers = voiceb.get_speaker_list()

        # ------------------------------------------------------
        # Create sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        # Create sidebar label
        self.side_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                 text='Options',
                                                 font=customtkinter.CTkFont(size=30, weight="bold"))
        self.side_label.grid(row=0, column=0, padx=20, pady=(15, 20))

        # Create and add optionmenu to sidebar frame
        def create_combobox(frame, var_name, row, option_list=None):
            if option_list is None:
                option_list = ['']
            label = customtkinter.CTkLabel(frame, text=f"{var_name}", anchor='w', font=customtkinter.CTkFont(size=18))
            label.grid(row=row, column=0, padx=20, pady=(10, 0))

            combobox_var = tk.StringVar()
            option_menu = ttk.Combobox(frame, textvariable=combobox_var, values=option_list, state='readonly')
            option_menu.set(option_list[0])
            option_menu.grid(row=row+1, column=0, padx=20, pady=(10, 0))

            return label, option_menu, combobox_var

        self.voice_name_label, self.voice_name_combobox, self.voice_name_variable = \
            (create_combobox(self.sidebar_frame, 'Voice Name', 1,
                             option_list=[name for entry in self.speakers for name in entry]))

        self.voice_style_label, self.voice_style_combobox, self.voice_style_variable = \
            (create_combobox(self.sidebar_frame, 'Voice Styles', 3, ['Select a voice first']))
        self.voice_name_variable.trace_add('write', self.update_styles)

        self.language_label, self.language_combobox, self.language_variable = \
            (create_combobox(self.sidebar_frame, 'TTS Language', 5, list(self.languages.keys())))
        # ------------------------------------------------------
        # Translate switch and label
        self.voice_translate_label = customtkinter.CTkLabel(self.sidebar_frame, text=f"Start\nTranslating",
                                                            anchor='w',
                                                            font=customtkinter.CTkFont(size=18))
        self.voice_translate_label.grid(row=7, column=0, padx=20, pady=(110, 10))
        self.voice_translate_switch = customtkinter.CTkSwitch(self.sidebar_frame, text='', switch_width=140,
                                                              button_color='DodgerBlue2',
                                                              button_length=25,
                                                              fg_color='firebrick4',
                                                              progress_color='medium sea green',
                                                              onvalue=1,
                                                              offvalue=0,
                                                              command=self.process_audio
                                                              )
        self.voice_translate_switch.grid(row=9, column=0, padx=(20, 5))

        # ------------------------------------------------------
        # Create sliders  frame
        self.sliders_frame = customtkinter.CTkFrame(self, corner_radius=15, border_width=2)
        self.sliders_frame.grid(row=0, column=1, sticky="nsew", padx=(25, 25), pady=(5, 0))
        self.sliders_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.sliders_frame.grid_rowconfigure((1, 2), weight=1)
        # Create sliders label
        self.sliders_label = customtkinter.CTkLabel(self.sliders_frame,
                                                    text='Voice configuration',
                                                    font=customtkinter.CTkFont(size=30, weight="bold"),
                                                    anchor='center')
        self.sliders_label.grid(row=0, pady=(5, 0), columnspan=6)

        # Create and add sliders to sliders frame
        def create_slider(slider_frame, var_name, init_value, column):
            def slider_value(value, label_text, var):
                label_text.configure(text=f'{var} {value:.1f}')
                return value

            var_label = f'{var_name}:'
            label = customtkinter.CTkLabel(slider_frame, text=f"{var_label} {init_value:.1f}", anchor="center")
            label.grid(row=2, column=column, pady=(0, 10))

            slider = customtkinter.CTkSlider(slider_frame,
                                             from_=0, to=5,
                                             orientation='vertical',
                                             button_hover_color='white',
                                             command=lambda value: slider_value(value, label, var_label))
            slider.grid(row=1, column=column, )

            slider.set(init_value)

            return slider, label
        self.speed_slider, self.speed_label = \
            create_slider(self.sliders_frame, 'Speed', 1.0, 0)
        self.pitch_slider, self.pitch_label = \
            create_slider(self.sliders_frame, 'Pitch', 0.0, 1)
        self.intonation_slider, self.intonation_label = \
            create_slider(self.sliders_frame, 'Intonation', 1.0, 2)
        self.volume_slider, self.volume_label = \
            create_slider(self.sliders_frame, 'Volume', 4.0, 3)
        self.pre_phoneme_slider, self.pre_phoneme_label = \
            create_slider(self.sliders_frame, 'Pre-phonemic\nPause', 1.0, 4)
        self.post_phoneme_slider, self.post_phoneme_label = \
            create_slider(self.sliders_frame, 'Post-phonemic\nPause', 1.0, 5)
        # ------------------------------------------------------
        # Create translation  frame
        self.translation_frame = customtkinter.CTkFrame(self, corner_radius=15, border_width=2)
        self.translation_frame.grid(row=1, column=1, rowspan=3, sticky="nsew", padx=(25, 25), pady=(5, 5))
        self.translation_frame.grid_columnconfigure(0, weight=1)
        self.translation_frame.grid_columnconfigure(1, weight=0)
        self.translation_frame.grid_rowconfigure(1, weight=1)
        # Create entry
        self.entry = customtkinter.CTkEntry(self.translation_frame, placeholder_text="Text to speech...")
        self.entry.grid(row=0, column=0, padx=(15, 0), pady=(10, 0), sticky='we', columnspan=1)
        # Create buttons for tts
        self.send_manual_input = customtkinter.CTkButton(self.translation_frame,
                                                         text='TTS',
                                                         command=self.process_tts)
        self.send_manual_input.grid(row=0, column=1, padx=(15, 15), pady=(10, 0), sticky='e')
        # Create data audio_files
        self.log_text = customtkinter.CTkTextbox(self.translation_frame)
        self.log_text.grid(row=1, column=0, padx=(15, 15), pady=(10, 10), sticky='nsew', columnspan=2)
        self.log_text.insert('0.0', 'System ready, record an audio or send a text...')
        self.log_text.configure(state='disabled')
        # ------------------------------------------------------

    # Functions
    def log_text_update(self, text):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f'\n{text}')
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def update_styles(self, *args):
        selected_name = self.voice_name_variable.get()
        styles_for_name = [entry[selected_name] for entry in self.speakers if selected_name in entry][0]
        self.voice_style_combobox['values'] = list(styles_for_name.keys())
        self.voice_style_combobox.current(0)

    def generate_ai_voice(self, translated_text, processing_done):
        def get_style_id(formatted_data, name, style):
            for entry in formatted_data:
                if list(entry.keys())[0] == name:
                    return entry[name].get(style)
            return None

        if self.voice_style_combobox.get() == 'Select a voice first':
            self.log_text_update('ERROR: No style selected, please select one.')
        else:
            voiceb.speak(speaker_id=get_style_id(self.speakers,
                                                 self.voice_name_combobox.get(),
                                                 self.voice_style_combobox.get()),
                         sentence=translated_text,
                         speed=self.speed_slider.get(),
                         pitch=self.pitch_slider.get(),
                         intonation=self.intonation_slider.get(),
                         volume=self.volume_slider.get(),
                         prephoneme=self.pre_phoneme_slider.get(),
                         postphoneme=self.post_phoneme_slider.get()
                         )
        processing_done.set()
        self.log_text_update('Done')

    def process_tts(self):
        try:
            language = self.language_combobox.get()
            text = self.entry.get()
            translated_text = ''
            if text != '':
                if language == 'Auto':
                    language, language_code = libre.detect_language(text)
                    if language is None:
                        self.log_text_update('Language detected not supported, select one from the list.')
                    else:
                        self.log_text_update(f'Language detected: {language}.')
                        translated_text = libre.translate_text(text=text, language=language_code)
                else:
                    translated_text = libre.translate_text(text=text, language=self.languages[language])

                self.log_text_update(f'Translated text: {translated_text}')
                processing_done = threading.Event()
                audio_thread = threading.Thread(target=self.generate_ai_voice,
                                                args=(translated_text, processing_done))
                audio_thread.start()
            else:
                self.log_text_update('ERROR: No text detected for TTS.')

        except KeyError:
            self.log_text_update('ERROR: You have to select a voice and style first.')

    def process_audio(self):
        switch_state = self.voice_translate_switch.get()
        key = "T"  # You can change this to any key you prefer.
        if switch_state == 1:
            self.send_manual_input.configure(state='disabled')
            self.entry.configure(state='disabled')
            recording_loop_thread = threading.Thread(target=self.monitor_and_record_audio,
                                                     args=(key, "audio_files/input_audio.wav"))
            self.log_text_update(f"Tss disabled.\nRecording enabled.\nHold '{key}' to start recording."
                                 f"\nThe process may take some time to complete.")

            recording_loop_thread.start()
        else:
            self.send_manual_input.configure(state='normal')
            self.entry.configure(state='normal')
            self.log_text_update('Tss enabled.')

    def monitor_and_record_audio(self, key, file_destination):
        while self.voice_translate_switch.get() == 1:

            time.sleep(0.1)
            # Recording audio
            input_audio.record_and_save_audio(key, file_destination)
            # Transcribing audio
            transcribed_text = speech_to_text(file_destination)
            self.log_text_update(f"Audio transcription: {transcribed_text}")
            language, language_code = libre.detect_language(transcribed_text)

            if language is None:
                self.log_text_update('Language detected not supported.')
            else:
                self.log_text_update(f"Language detected: {language}.")
                # Translating transcription
                translated_text = libre.translate_text(text=transcribed_text, language=language_code)
                self.log_text_update(f'Translated text: {translated_text}')
                processing_done = threading.Event()
                # Playing translated text
                audio_thread = threading.Thread(target=self.generate_ai_voice,
                                                args=(translated_text, processing_done))
                audio_thread.start()

            # A small delay to prevent high CPU usage.
            time.sleep(0.1)
