import oauth2client
import httplib2
import pprint
import json
import base64
import numpy as np
import soundfile

from pydub import AudioSegment
from pydub.playback import play

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

fp = open('words.json', 'r')
words = json.loads(fp.read())
fp.close()

credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "auth.json",
        scopes="https://www.googleapis.com/auth/cloud-platform")

http = httplib2.Http()
http = credentials.authorize(http)

voice_names = [
        'nl-NL-Standard-A',
        'nl-NL-Standard-B',
        'nl-NL-Standard-C',
        'nl-NL-Standard-D',
        'nl-NL-Standard-E',
        'nl-NL-Wavenet-A',
        'nl-NL-Wavenet-B',
        'nl-NL-Wavenet-C',
        'nl-NL-Wavenet-D',
        'nl-NL-Wavenet-E',
        ]

genders = ['MALE', 'FEMALE']

def get_body(word, voice_name, gender):
    return {
            "audioConfig": {
                "audioEncoding": "LINEAR16",
                "effectsProfileId": [],
                "pitch": -0.0,
                "sampleRateHertz": 24000,
                "speakingRate": 1.0,
                "volumeGainDb": -10.0
                },
            "input": {
                "text": word
                },
            "voice": {
                "languageCode": "nl-NL",
                "name": "%s" % voice_name,
                "ssmlGender": "%s" % gender,
                }
            }


with build('texttospeech', 'v1', http=http) as service:
    voices = service.voices().list().execute(http=http)
    voices = list(filter(lambda v: v['languageCodes'].pop().startswith('nl-NL'), voices['voices']))

    for voice_name in voice_names:
        for gender in genders:
            for word in words:
                word = word.strip()
                w = '%s, %s. %s.. %s! %s? %s-%s' % (word, word, word, word, word, word, word)
                result = service.text().synthesize(body=get_body(w, voice_name, gender)).execute(http=http)
                audio = base64.b64decode(result['audioContent'])

                with open('output/%s|%s|%s.wav' % (w, voice_name, gender), 'wb') as fp:
                    fp.write(audio)
