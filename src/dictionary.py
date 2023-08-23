import os
from glob import glob
import librosa
import numpy as np
import matplotlib.pyplot as plt


class Dictionary:

    data = {}

    root = ''

    def __init__(self, root: str, init: bool = False):
        super().__init__()

        self.root = os.path.realpath(root)

        if init:
            self.init()
        else:
            fp = os.path.join(self.root, 'dataset.npz')
            if os.path.isfile(fp):
                self.open(fp)

    def init(self):
        self.data = {'input': [], 'refs': {}}
        fp = os.path.join(self.root, 'words.json')
        print(f'Reading labels from: {fp}..')


        print('Reading reference audio files..')
        seen = []
        for fp in glob(os.path.join(self.root, 'audio', '*.wav')):
            label = os.path.basename(fp).split(',')[0]
            self.data[label] = {}

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
                env = librosa.effects.feature.poly_features(y=ref, sr=sr, order=2)
                sounds.append(ref)
                envelopes.append(env)

            self.data['refs'][label] = np.array({'sounds': sounds, 'envelopes': envelopes})

        seen = []
        print('Reading input audio files..')
        for fp in glob(os.path.join(self.root, 'input', '**', '*aac.wav')):
            if fp.find('entropy') + fp.find('peaks') + fp.find('processed') + fp.find('normalized') + fp.find('snippet') >= 0:
                continue

            sound, sr = librosa.load(fp, mono=True)
            sound = librosa.util.normalize(sound)

            hsh = hash(sound.tostring())
            if hsh in seen:
                continue
            seen.append(hsh)

            print(fp)

            env = librosa.effects.feature.poly_features(y=sound, sr=sr, order=2)
            self.data['input'].append(np.array({'sound': sound, 'envelope': env}))

        fp = os.path.join(self.root, 'dataset.npz')
        print(f'Writing initial dataset to: {fp}..')
        np.savez_compressed(fp, refs=self.data['refs'], input=self.data['input'])
        self.data = self.data

    def open(self, filename: str):
        print(f'Opening dataset: {filename}..')

        npz = np.load(filename, allow_pickle=True)
        self.data['refs'] = npz['refs']
        self.data['input'] = npz['input']

        print(self.data['refs'][0])

        ref_env = self.data['refs'][0]['Computer'][0]['envelopes'][0]
        snd_env = self.data['input'][0]['envelope']

        plt.figure(1)

        plt.subplot(211)
        t = np.linspace(0., ref_env.size / 22050, ref_env.size)
        plt.plot(t, ref_env)

        plt.subplot(212)
        t = np.linspace(0., snd_env.size / 22050, snd_env.size)
        plt.plot(t, snd_env)

        plt.show()

        print(self.data)

    @property
    def refs(self) -> dict:
        return self.data.get('refs')




