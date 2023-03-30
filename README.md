# MyVoiceTranslator
![gui image](https://i.imgur.com/kZNjwyU.png)

I wanted to make a little project working with a couple of AI's, with MvT you can talk directly
to the microphone or use TTS and it will translate and play what you said in Japanese with the use of the following AI's:

1. [LibreTranslate] AI powered translation tool.
2. [WhisperAI] speech recognition model from OpenAi.
3. [Voicevox] japanese voice synthesizer with plenty of choices.

An intuitive GUI has been developed so you don't need to deal with the API's.

## Instructions
- Download Docker-Desktop
- Download the repo
- Run the requirements.txt
- Run:
  ```
  docker-compose -f ./docker-compose.mvt.yml up --build
  ```
- Run the script and follow the instructions

### To-do
There are still quite a few bugs and exceptions I need to catch and fix, I realized mid development that the structure
I was using to manage the data was very inefficient, but fixing it would require remaking everything and it will take time.

I wanted to implement a menu to set some env variables to select virtual input and output devices so you could directly
 play the audio on another app.

This project was inspired by [this video](https://youtu.be/UY7sRB60wZ4) from @SociallyIneptWeeb.
