from pycipher import Caesar


class CaesarBreak(object):
    def __init__(self, scorer):
        self.scorer = scorer
        self.alphabet_size = 26

    def best_guess(self, text):
        plaintext, _, _ = self.guess(text, 1)[0]
        return plaintext

    def guess(self, text, n=3):
        return [(self.decipher(text, key), score, chr(key + 65))
                for key, score in self.scores(text)][:n]

    def analyse(self, text):
        guesses = self.guess(text, n=self.alphabet_size)
        print("")
        print("Analysing {}\n...".format(text))
        for guess in guesses:
            decryption, score = guess
            print("score: {} - plaintext: {}".format(score, decryption))
        print("")

    def best(self, text):
        return self.scores(text)[0]

    def scores(self, text):
        scores = [(i, self.scorer.score(self.decipher(text, i)))
                  for i in range(self.alphabet_size)]
        return sorted(scores, reverse=True, key=lambda t: t[1])

    def decipher(self, text, key):
        return Caesar(key).decipher(text)


if __name__ == "__main__":
    import sys
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "..", ".."))
    from cryptanalysis.util.transforms import Masker
    from cryptanalysis.data.en import load_ngrams
    from cryptanalysis.score.ngram import NgramScorer
    scorer = NgramScorer(load_ngrams(1))

    plaintext = "Hello World, how are you doing right now?"
    ciphertext = "Vszzc Kcfzr, vck ofs mci rcwbu fwuvh bck?"  # key = 14
    print("Plaintext: {}\nCiphertext: {}" .format(plaintext, ciphertext))

    masker = Masker(ciphertext, r"[a-zA-Z]")
    ciphertext = masker.reduce()
    print("Masked ciphertext: {}".format(ciphertext))

    breaker = CaesarBreak(scorer)
    breaker.analyse(ciphertext)
    best_3_guesses = breaker.guess(ciphertext, 3)
    for i, guess in enumerate(best_3_guesses):
        decryption, score = guess
        print("Decryption candidate {} ({}): {}"
              .format(i, score, masker.extend(decryption)))
