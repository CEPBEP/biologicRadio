import sys
from os import path
from argparse import ArgumentParser

from src import Classifier, Dictionary, Generator

parser = ArgumentParser()
parser.add_argument('-i', '--init', required=False, action='store_true')
parser.add_argument('-w', '--wordlist', required=False, type=str)

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])

    data_dir = path.join(path.dirname(__file__), 'data')

    gr = Generator(wordlist=args.wordlist if args.wordslist is not None else path.join(data_dir, 'words.json'))
    ds = Dictionary(data_dir, init=args.init)
    cf = Classifier(dictionary=ds)
