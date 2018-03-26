import speech_recognition as sr
from gtts import gTTS
from  pyrecipe.recipe import Recipe
r = sr.Recognizer()

def get_speech():
    r = sr.Recognizer()
    with sr.Microphone(device_index=6) as source:
        try:
            r.adjust_for_ambient_noise(source)
            print('say something')
            audio = r.listen(source)
            text = r.recognize_google(audio)

            if text == "next ingredient":
                print('Going to next ingredient')
            else:
                print('Still waiting, {} is not a good response'.format(text))
        except sr.UnknownValueError:
            print('I am sorry, I did not understand you')
            exit()

def text_ts():
    r = Recipe('chicken and sausage gumbo')
    method = r.get_method()
    text = '. '.join(method)
    tts = gTTS(text=text, lang='en')
    tts.save('test.mp3')
text_ts()
