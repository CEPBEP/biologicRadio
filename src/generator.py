import httplib2
import os
import json
import base64

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build


class Generator:

    voice_names = ['nl-NL-Standard-A',
                   'nl-NL-Standard-B',
                   'nl-NL-Standard-C',
                   'nl-NL-Standard-D',
                   'nl-NL-Standard-E']

    genders = ['MALE', 'FEMALE']

    def __init__(self, wordlist: str):
        super().__init__()

        with open(os.path.realpath(wordlist), 'r') as fp:
            self.words = json.loads(fp.read())

    def generate_word_samples(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "auth.json",
            scopes="https://www.googleapis.com/auth/cloud-platform")

        http = credentials.authorize(httplib2.Http())

        with build('texttospeech', 'v1', http=http) as service:
            for voice_name in self.voice_names:
                for gender in self.genders:
                    for word in self.words:
                        word = word.strip()
                        w = '%s, %s. %s.. %s! %s?' % (word, word, word, word, word)
                        result = service.text().synthesize(body=self.get_body(w, voice_name, gender)).execute(http=http)
                        audio = base64.b64decode(result['audioContent'])

                        with open('dictionary/%s|%s|%s.wav' % (w, voice_name, gender), 'wb') as fp:
                            fp.write(audio)

    @staticmethod
    def get_body(word: str, voice_name: str, gender: str):
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
