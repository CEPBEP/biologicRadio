import httplib2
import os
import json
import base64

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build


class DictionaryGenerator:

    def __init__(self, data_dir: str, auth_file: str, wordlist: str, locale_code: str):
        super().__init__()

        self.auth_file = auth_file
        self.data_dir = data_dir
        self.voice_info = self.get_voice_info(locale_code)

        with open(os.path.realpath(wordlist), 'r') as fp:
            self.words = json.loads(fp.read())

    @property
    def voices(self):
        return self.voice_info

    def build_http(self):
        return ServiceAccountCredentials.from_json_keyfile_name(
            self.auth_file,
            scopes='https://www.googleapis.com/auth/cloud-platform').authorize(httplib2.Http())

    def generate_word_samples(self):
        http = self.build_http()
        with build('texttospeech', 'v1', http=http) as service:
            for voice in self.voice_info:
                for word in self.words:
                    voice_name = voice.get('name')
                    voice_gender = voice.get('ssmlGender')
                    word = word.strip()

                    print(f'Generating word sample "{word}" with voice "{voice_name}" for gender "{voice_gender}..')

                    body = self.get_body('<speak>%s, %s. %s.. %s! %s?</speak>' % (word, word, word, word, word),
                                         voice)

                    result = service.text().synthesize(body=body).execute(http=http)

                    fp = os.path.join(self.data_dir, 'dictionary',
                                      '%s|%s|%s.wav' % (word, voice_name, voice_gender))

                    with open(fp, 'wb') as fp:
                        fp.write(base64.b64decode(result['audioContent']))

    @staticmethod
    def get_body(ssml: str, voice: dict):
        return {'audioConfig': {
            'audioEncoding': 'LINEAR16',
            'effectsProfileId': [],
            'pitch': -0.0,
            'sampleRateHertz': voice.get('naturalSampleRateHertz'),
            'speakingRate': 1.0,
            'volumeGainDb': -10.0},
            'input': {
                'ssml': ssml},
            'voice': {
                'languageCode': voice.get('languageCodes')[0],
                'name': '%s' % voice.get('name'),
                'ssmlGender': '%s' % voice.get('ssmlGender')}}

    def get_voice_info(self, locale_code: str):
        http = self.build_http()
        with build('texttospeech', 'v1', http=http) as service:
            return list(filter(lambda v: locale_code in v['languageCodes'],
                               service.voices().list().execute(http=http)['voices']))

