import sys
from os import path
from argparse import ArgumentParser

from src import Classifier, Dictionary

parser = ArgumentParser()
parser.add_argument('-i', '--init', required=False, action='store_true')

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])
    ds = Dictionary(path.join(path.dirname(__file__), 'data'), init=args.init)
    cf = Classifier(dictionary=ds)