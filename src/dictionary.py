import base64
import httplib2
import json
import librosa
import os
import soundfile

import matplotlib.pyplot as plt
import numpy as np

from glob import glob
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from scipy.signal import hilbert, savgol_filter


class Dictionary:

    _data = None

    def __init__(self,
                 data_dir: str,
                 generate: bool,
                 auth_file: str,
                 wordlist: str,
                 locale_code: str,
                 voice_models: list,
                 force: bool):

        super().__init__()

        self.data_dir = data_dir
        self.dataset_dir = os.path.join(self.data_dir, 'dataset')
        self.auth_file = auth_file
        self.force = force

        self._voices = self.get_voice_info(locale_code, voice_models)

        with open(wordlist, 'r') as fp:
            self.words = json.loads(fp.read())

        if generate:
            self.init()
        else:
            fp = os.path.join(self.data_dir, 'dataset.bin')
            try:
                self.open(fp)
            except FileNotFoundError:
                raise FileNotFoundError(f'"{fp}", regenerate it by passing -g / --generate')

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def voices(self):
        return self._voices

    def build_http(self):
        return ServiceAccountCredentials.from_json_keyfile_name(
            self.auth_file,
            scopes='https://www.googleapis.com/auth/cloud-platform').authorize(httplib2.Http())

    def generate_word_samples(self):
        fp_gen_completed = os.path.join(self.data_dir, '.generation_completed')
        if os.path.isfile(fp_gen_completed) and not self.force:
            print('Skipping word sample generation, already completed, pass --force to override.')
            return

        if os.path.isfile(fp_gen_completed):
            os.remove(fp_gen_completed)

        for fp in glob(os.path.join(self.data_dir, 'dictionary', '*.wav')):
            os.remove(fp)

        http = self.build_http()
        with build('texttospeech', 'v1', http=http) as service:
            for voice in self._voices:
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

        with open(fp_gen_completed, 'w') as fp:
            fp.write('')

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

    def get_voice_info(self, locale_code: str, voice_models: list):
        http = self.build_http()
        with build('texttospeech', 'v1', http=http) as service:
            voices = service.voices().list().execute(http=http)['voices']
            if len(voice_models) == 1:
                for voice_model in voice_models:
                    voices = list(filter(lambda v: v.get('name').lower().find(voice_model) != -1, voices))

            return list(filter(lambda v: locale_code in v['languageCodes'], voices))

    def init(self):
        print('Generating word samples..')
        self.generate_word_samples()

        print('Creating word sample dataset..')
        if not os.path.isdir(self.dataset_dir):
            os.mkdir(self.dataset_dir)

        data = {}
        seen = []
        for fp in glob(os.path.join(self.data_dir, 'dictionary', '*.wav')):
            label, voice, gender = list(map(lambda v: v.lower(), os.path.basename(fp).split('|')))

            sound, sr = librosa.load(fp, mono=True, sr=24000)

            hsh = hash(sound.tostring())
            if hsh in seen:
                continue
            seen.append(hsh)

            sound = librosa.util.normalize(sound)

            word_dir = os.path.join(self.dataset_dir, f'{label}-{voice}-{gender}')
            if not os.path.isdir(word_dir):
                os.mkdir(word_dir)

            print(label)

            splits = librosa.effects.split(sound, frame_length=512)
            if len(splits) < 5:
                print(f'Number of splits is not 5 for file "{fp}", skipping..')
                continue

            data[label] = {'samples': [], 'envelopes': []}
            for i, split in enumerate(splits):
                sample = sound[split[0]:split[1]]
                soundfile.write(os.path.join(word_dir, f'{i}.wav'), sample, samplerate=int(sr))
                inst_ampl = np.abs(hilbert(sample))
                envelope = savgol_filter(inst_ampl, 512, 2)
                soundfile.write(os.path.join(word_dir, f'{i}-envelope.wav'), envelope, samplerate=int(sr))

    def open(self, filename: str):
        pass
        # plt.figure(1)
        #
        # plt.subplot(211)
        # t = np.linspace(0., item['samples'][0].size / 24000, item['samples'][0].size)
        # plt.plot(t, item['samples'][0])
        #
        # plt.subplot(212)
        # t = np.linspace(0., item['envelopes'][0].size / 24000, item['envelopes'][0].size)
        # plt.plot(t, item['envelopes'][0])
        #
        # plt.show()
