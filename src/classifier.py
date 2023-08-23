import numpy as np
import librosa

from .dictionary import Dictionary


class Classifier:
    def __init__(self, dictionary: Dictionary):
        super().__init__()

        self.dictionary = dictionary

    def label_words(self, filename: str):
        sound, sr = librosa.load(filename, mono=True)
        sound = librosa.util.normalize(sound)
        env = librosa.effects.feature.poly_features(y=sound, sr=sr, order=2)

        scores = []
        for ref in self.dictionary.refs:
            scores.append(self.match_word(env, ref))

    @staticmethod
    def match_word(database: np.ndarray, sample: list):
        sample_scores = []
        for sample in sample['envelopes'][:-1]:
            d, wp = librosa.sequence.dtw(X=database, Y=sample, subseq=True)
            sample_scores.append(d[-1, -1])

        return np.mean(sample_scores)




