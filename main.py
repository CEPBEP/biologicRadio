import sys
from os import path
from argparse import ArgumentParser

from src import Classifier, Dictionary, DictionaryGenerator

parser = ArgumentParser()
parser.add_argument('-i', '--init', required=False, action='store_true', help='Initialize dataset using Google TTS Api')
parser.add_argument('-w', '--wordlist', required=False, type=str, help='path to wordlist.json for Google TTS Api')
parser.add_argument('-a', '--auth', required=False, type=str, help='path to auth.json for Google TTS Api')
parser.add_argument('--list-voices', required=False, action="store_true", help='List voices from Google TTS Api')
parser.add_argument('--locale-code', required=False, type=str, help='Set locale code for Google TTS Api',
                    default='en-US')

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])

    root = path.realpath(path.join(path.dirname(__file__), 'data'))

    gr = DictionaryGenerator(data_dir=root,
                             wordlist=args.wordlist if args.wordlist is not None
                             else path.join(root, 'words.json'),
                             auth_file=args.auth if args.auth is not None
                             else path.join(root, 'auth.json'),
                             locale_code=args.locale_code)

    if args.list_voices:
        print(gr.voices)

        sys.exit(0)

    cf = Classifier(dictionary=Dictionary(data_dir=root, init=args.init, generator=gr))
