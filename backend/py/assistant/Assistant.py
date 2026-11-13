import os
import time
import playsound
import speech_recognition as sr
from gtts import gTTS
import control.device_commands as dc


class Assistant:

    def __init__(self, device_commands: dc):
        self.device_commands = device_commands

    def assistant_loop(self):
        
        # lyssna efter röst kommando

        print("lisening")
        audio = self.get_audio()

        print(audio);

        # om röst

        if(audio != ""):
            # parsa kommando
            command = self.text_to_command()
            
            # exekvera kommando
            if(command):
                pass
                # self.device_commands.

        time.sleep(0.1) 
        

    def text_to_command(text):
        pass
    
    def speak(self, text):
        print("speaking...", text)
        tts = gTTS(text=text, lang='en')
        # filename = 'voice.mp3'
        filename = os.path.join(os.getcwd(), 'voice.mp3')
        tts.save(filename)

        time.sleep(1)

        playsound.playsound(filename)
        os.remove(filename)

    def get_audio(self):
        r = sr.Recognizer()

        with sr.Microphone() as source:
            
            # r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

            try:
                said = r.recognize_google(audio)
                # if(said == 'hello Bixby'):
                    # self.speak("Hello Oskar!")

                return said

            except Exception as e:
                return ""

if __name__ == '__main__':
    print("Starting Bixby...")
    assistant = Assistant()
    assistant.speak("Hello! I'm Bixby, your new assistant")
    assistant.get_audio()

    while True:
        assistant.assistant_loop()