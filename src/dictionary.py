import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import pickle
import gzip

from glob import glob
from .dictionary_generator import DictionaryGenerator

class Dictionary:

    data = None

    data_dir = ''

    def __init__(self, data_dir: str, generator: DictionaryGenerator, init: bool = False):
        super().__init__()

        self.data_dir = os.path.realpath(data_dir)
        self.generator = generator

        if init:
            self.generator.generate_word_samples()
            self.init()
        else:
            fp = os.path.join(self.data_dir, 'dataset.bin')
            if os.path.isfile(fp):
                self.open(fp)

    def init(self):
        data = {}

        print('Reading reference audio files..')
        seen = []
        for fp in glob(os.path.join(self.data_dir, 'audio', '*.wav')):
            label = os.path.basename(fp).split(',')[0]
            data[label] = {}

            sound, sr = librosa.load(fp, mono=True)
            sound = librosa.util.normalize(sound)

            hsh = hash(sound.tostring())
            if hsh in seen:
                continue
            seen.append(hsh)

            print(fp)

            splits = librosa.effects.split(sound)
            sounds = []
            envelopes = []
            for split in splits:
                ref = sound[split[0]:split[1]]
                sounds.append(ref)
                envelopes.append(librosa.effects.feature.poly_features(y=ref, sr=sr, order=2))

            data[label] = {'sounds': sounds, 'envelopes': envelopes}

        fp = os.path.join(self.data_dir, 'dataset.bin')
        print(f'Writing initial dataset to: {fp}..')
        with open(fp, 'wb') as fp:
            zipped = gzip.compress(pickle.dumps(data), 9)
            fp.write(zipped)

        self.data = data

    def open(self, filename: str):
        print(f'Opening dataset: {filename}..')

        fp = os.path.join(self.data_dir, 'dataset.bin')
        with gzip.open(fp) as fp:
            self.data = pickle.loads(fp.read())

        # plt.figure(1)
        #
        # plt.subplot(211)
        # t = np.linspace(0., ref_env.size / 22050, ref_env.size)
        # plt.plot(t, ref_env)
        #
        # plt.subplot(212)
        # t = np.linspace(0., snd_env.size / 22050, snd_env.size)
        # plt.plot(t, snd_env)
        #
        # plt.show()

        print(self.data)

    @property
    def refs(self) -> dict:
        return self.data.get('refs')




