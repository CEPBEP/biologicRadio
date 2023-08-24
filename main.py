import sys
from os import path
from argparse import ArgumentParser

from src import Classifier, Dictionary

data_dir = path.realpath(path.join(path.dirname(__file__), 'data'))

parser = ArgumentParser()
parser.add_argument('-f', '--file', required=False, type=str,
                    help='Path to audiofile to run dynamic time-warping on against word samples')
parser.add_argument('-g', '--generate', required=False, action='store_true', help='Generate word sample dataset')
parser.add_argument('--force', required=False, action='store_true', help='Force re-generation of word samples.')
parser.add_argument('--wordlist', required=False, type=str, default='words.json',
                    help='path to wordlist.json for Google TTS Api')
parser.add_argument('--auth-file', required=False, type=str, default='auth.json',
                    help='path to auth.json for Google TTS Api')
parser.add_argument('--list-voices', required=False, action='store_true', help='List voices from Google TTS Api')
parser.add_argument('--voice-model', required=False, nargs='+', choices=['wavenet', 'standard'], default='wavenet',
                    help='Voice model for Google TTS Api')
parser.add_argument('--locale-code', required=False, type=str, help='Set locale code for Google TTS Api',
                    default='en-US')

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])

    voice_models = []
    for x in args.voice_model:
        if x not in voice_models:
            voice_models.append(x)

    wordlist = path.realpath(args.wordlist) if (args.wordlist is not None and path.isfile(args.wordlist)) \
        else path.realpath(path.join(data_dir, 'words.json'))

    auth_file = path.realpath(args.auth_file) if (args.auth_file is not None and path.isfile(args.auth_file)) \
        else path.realpath(path.join(data_dir, 'auth.json'))

    dictionary = Dictionary(data_dir=data_dir,
                            generate=args.generate,
                            wordlist=wordlist,
                            auth_file=auth_file,
                            locale_code=args.locale_code,
                            voice_models=voice_models,
                            force=args.force)

    if args.list_voices:
        print(dictionary.voices)

        sys.exit(0)

    if args.file:
        cf = Classifier(dictionary=dictionary)
        result = cf.label_words(path.realpath(args.file))
