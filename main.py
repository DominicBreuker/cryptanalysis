from pycipher import Caesar
from breaking.caesar import CaesarBreak

from pycipher import Vigenere
from breaking.vigenere import KeylengthDetector
from breaking.vigenere import VigenereBreak

from pycipher import SimpleSubstitution
from breaking.substitution import SubstitutionBreak

from util.transforms import Masker
from score.ioc import IocScorer
from data.en import load_ngrams
from score.ngram import NgramScorer


def break_caesar_example(plaintext, masker):
    print("#######################################")
    print("######## Caesar cipher example ########")
    print("#######################################")

    key = 13
    ciphertext = Caesar(key).encipher(plaintext)

    print("\nCiphertext:\n---")
    print(masker.extend(ciphertext))
    print("---\n")

    print("\nCracking...\n")
    scorer = NgramScorer(load_ngrams(3))
    breaker = CaesarBreak(scorer)
    decryption, score, key = breaker.guess(ciphertext, 1)[0]
    print("Caesar decryption (key={}, score={}):\n---\n{}---\n"
          .format(key, score, masker.extend(decryption)))


def break_vigenere_example(plaintext, masker):
    print("#########################################")
    print("######## Vigenere cipher example ########")
    print("#########################################")

    key = "somekey"
    ciphertext = Vigenere(key).encipher(plaintext)

    print("\nCiphertext:\n---")
    print(masker.extend(ciphertext))
    print("---\n")

    print("\nCracking...\n")

    print("Inferring key length...")
    s = IocScorer(alphabet_size=26)
    KeylengthDetector(s).detect(ciphertext)

    print("Cracking with key length 7... (11 was false positive)")

    scorer = NgramScorer(load_ngrams(1))
    breaker = VigenereBreak(7, scorer)
    decryption, score, key = breaker.guess(ciphertext)[0]
    print("Vigenere decryption (key={}, score={}):\n---\n{}---\n"
          .format(key, score, masker.extend(decryption)))


def break_substitution_example(plaintext, masker):
    print("#############################################")
    print("######## Substitution cipher example ########")
    print("#############################################")

    key = ['L', 'C', 'N', 'D', 'T', 'H', 'E', 'W', 'Z', 'S', 'A', 'R', 'X',
           'V', 'O', 'J', 'B', 'P', 'F', 'U', 'I', 'Q', 'M', 'K', 'G', 'Y']
    ciphertext = SimpleSubstitution(key).encipher(plaintext)

    print("\nCiphertext:\n---")
    print(masker.extend(ciphertext))
    print("---\n")

    print("\nCracking...\n")
    scorer = NgramScorer(load_ngrams(4))
    breaker = SubstitutionBreak(scorer, seed=42)
    breaker.optimise(ciphertext, n=3)
    decryption, score, key = breaker.guess(ciphertext)[0]
    print("Substitution decryption (key={}, score={}):\n---\n{}---\n"
          .format(key, score, masker.extend(decryption)))


if __name__ == "__main__":
    with open("examples/text.txt", "r") as f:
        plaintext, masker = Masker.from_text(f.read())

    break_caesar_example(plaintext, masker)
    break_vigenere_example(plaintext, masker)
    break_substitution_example(plaintext, masker)
