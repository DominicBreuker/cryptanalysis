# cryptanalysis

These are a couple of scripts illustrating how to break classical ciphers.
Classical ciphers are ciphers that are not considered modern anymore.
Nobody actually uses them anymore.
This effort is just for fun :)

For a quick start, run `python main.py` and you can watch every supported cipher being broken once.

Currently, the following ciphers are supported:

## Caesar

In this cipher, all letters are shifted left through the alphabet.
The number of shifts is the key.
At the end of the alphabet, you go back to its beginning.
For example, if the key is 3, a plaintext "A" would become a "D" during encryption.

To break this cipher, you can simply try all 26 keys.
Score each resulting text by quality (similarity to english language) and you will find the plaintext.

## Vigenere

This cipher is a sophisticated version of the Caesar cipher.
You pick many Caesar cipher keys and apply them periodically.
If the Vigenere key is `[3, 16, 4]` then you shift the 1st, 4th, 7th, ... letter of the plaintext by three during encryption.
The 2nd, 5th, 8th, ... letter is shifted 16.
The 3rd, 6th, 9th, ... letter is shifted 4.

To break it, you must first find the length of the key.
A statistical technique can be used (Index of Coincidence - IoC).
In English text, the chance that two randomly choses letters are the same is different than in random text.
This is because in English, letters have uneven probabilities, some being more probable than others.
In random text, they have all the same probability.
Knowing the key length, you simply have to break many Caesar ciphers.


## Substitution

A substitution cipher shuffles the letters of the plaintext.
The key is a permutation of the alphabet and determines how to shuffle them.

To break the substitution cipher, you must try different keys and score their quality.
Trying all keys is impossible as their number is factorial in the alphabet size (e.g., 4.0329146e+26 keys for an alphabet size of 26).
You can use a hill climbing algorithm though to find locally optimal keys.
Start with a random key, then swap letters until you cannot improve anymore.
Starting multiple times with random initial keys gives you multiple local optima.
If one of them gives you a readable text, you are done!

# Tools

To break ciphers described above, you need a number of tools.

## Scorers

### Ngram Scorer

You must be able to score a candidate plaintext and check how good it is.
We define good in terms of "looks like english" and use ngram-based scoring.
In the folder `data`, there are lists of ngrams along with their empirical frequency in English text.
You can use them together `score/ngram.py` to check how likely a piece of text is given these frequencies.

### IoC Scorer

This scorer implements the Index of Coincidence metric described above for the Vigenere cipher.

## Utils

In the file `util/transforms`, there is a class `Masker` which allows you to strip of excess letters from ciphertext.
For instance, if your ciphertext comes as `Hgkke Frorl!` and your alphabet is `[A-Z]`, it turns the text into `HGKKEFRORL`.
After deciphering this to `HELLOWORLD` it can extend this string to `Hello World!` for easier reading.

# Examples

## Breaking Caesar cipher

Pick a ciphertext and break it using English trigram statistics.

```python
from data.en import load_ngrams
from score.ngram import NgramScorer
from breaking.caesar import CaesarBreak

ciphertext, masker = Masker.from_text("... your ciphertext ...")

scorer = NgramScorer(load_ngrams(3))
breaker = CaesarBreak(scorer)
decryption, score, key = breaker.guess(ciphertext, 1)[0]
print("Caesar decryption (key={}, score={}):\n---\n{}---\n"
      .format(key, score, masker.extend(decryption)))
```

## Breaking Vigenere cipher

Pick a ciphertext and break it using English trigram statistics.
To score the ciphertexts, you muse use monogram statistics.
Since the Vigenere cipher interleaves the Caesar ciphers, letters for each individual Caesar breaking run will not be consecutive English letters.

```python
from data.en import load_ngrams
from score.ngram import NgramScorer
from score.ioc import IocScorer
from breaking.vigenere import KeylengthDetector
from breaking.vigenere import VigenereBreak

ciphertext, masker = Masker.from_text("... your ciphertext ...")

s = IocScorer(alphabet_size=26)
KeylengthDetector(s).detect(ciphertext)

scorer = NgramScorer(load_ngrams(1)) #  must be 1, because Caesar ciphers are interleved
breaker = VigenereBreak(7, scorer)
decryption, score, key = breaker.guess(ciphertext)[0]
print("Vigenere decryption (key={}, score={}):\n---\n{}---\n"
      .format(key, score, masker.extend(decryption)))
```

## Breaking Substitution cipher

Pick a ciphertext and break it using English quadgram statistics.
We generate 3 local optima and print the best result.
If that does not deliver a solution, generate more local optima.
Each optimization run will print a short line with results.
You are looking for a score significatly better than most of the others that are printed.

```python
from data.en import load_ngrams
from score.ngram import NgramScorer
from breaking.substitution import SubstitutionBreak

scorer = NgramScorer(load_ngrams(4))
breaker = SubstitutionBreak(scorer)
breaker.optimise(ciphertext, n=3) #  try 3 times
decryption, score, key = breaker.guess(ciphertext)[0] #  see what best on delivers
print("Substitution decryption (key={}, score={}):\n---\n{}---\n"
      .format(key, score, masker.extend(decryption)))
```

# Acknowledgements

The code in this repository is inspired a lot by (this site)[http://practicalcryptography.com/].
Many thanks to the owner of it!
