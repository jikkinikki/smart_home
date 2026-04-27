import os
import time
import playsound
import speech_recognition as sr
from gtts import gTTS

class Assistant:
    
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
                print(said)

                # if(said == 'hello Bixby'):
                    # self.speak("Hello Oskar!")

                return said

            except Exception as e:
                print("Exception: " + str(e))
                return ""


    # speak("Hello Soori!")

    # speak("Hello! I'm Bixby, your new assistant")
    # get_audio()

if __name__ == '__main__':
    print("Starting Bixby...")
    assistant = Assistant()
    assistant.speak("Hello! I'm Bixby, your new assistant")
    assistant.get_audio()