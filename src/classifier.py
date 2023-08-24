import librosa
import numpy as np
import matplotlib.pyplot as plt
import soundfile

from scipy.signal import hilbert, savgol_filter

from .dictionary import Dictionary


class Classifier:
    def __init__(self, dictionary: Dictionary):
        super().__init__()

        self.dictionary: Dictionary = dictionary

    def label_words(self, filename: str):
        sound, sr = librosa.load(filename, mono=True, sr=24000)
        sound = librosa.util.normalize(sound)
        inst_ampl = np.abs(hilbert(sound))
        envelope = savgol_filter(inst_ampl, 1024, 2)

        soundfile.write(f'{filename}-envelope.wav', envelope, samplerate=int(sr))

        # scores = []
        # for item in self.dictionary.data().items():
        #     scores.append(self.match_word(envelope, item))

    @staticmethod
    def match_word(database: np.ndarray, sample: list):
        sample_scores = []
        for sample in sample['envelopes'][:-1]:
            d, wp = librosa.sequence.dtw(X=database, Y=sample, subseq=True)
            sample_scores.append(d[-1, -1])

        return np.mean(sample_scores)




