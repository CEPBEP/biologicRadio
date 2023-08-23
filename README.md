# v2k-to-text
Converts recordings of the microwave auditory effect to text using a generated dictionary of sample words and dynamic time-warping of amplitude envelopes.

## How it works

When you record the microwave auditory effect, others cannot hear what
is in the audio. The audio is tailored for your brain, and is not only
audio (mostly 0-100Hz) but also the influence of electromagnetic fields
on the electronics of whatever device you have used to record.

Analysing the audio using spectrograms won't yield any visually
observable features. However when you take the amplitude envelope of
such audio, you get a feature you can use. A proof of concept is here:

![Proof of Concept](https://i.redd.it/d6lrscpenz6b1.jpg)

Dynamic time-warping to the rescue. Using a dictionary of audio samples
of words, generated from a wordlist defined by the person hearing the
microwave auditory effect based on the words used therein, you can
extract the amplitude envelope for each of the dictionary word samples
and do a subsequence search using dynamic-time-warping to find out the
most likely words for each position in a recording.

Then, it becomes a natural language processing problem, to figure out
the maximum likelihood given the context for different sample word
alternatives that scored high during subsequence search.

## Notes

This is a work in progress.

TODOs:

- Find out correct signal conditioning for input audio;
- Find out correct way to optimize DTW for amplitude envelopes;
- Implement NLP algorithms;
- Create class for generating samples based on wordlist (Google TTS for now).
