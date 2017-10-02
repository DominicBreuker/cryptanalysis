from collections import OrderedDict
from .caesar import CaesarBreak


class VigenereBreak(object):
    def __init__(self, key_length, scorer=None):
        self.key_length = key_length
        self.caesar_breaker = CaesarBreak(scorer)

    def analyse(self, text):
        guesses = self.guess(text)
        print("")
        print("Analysing for Vigenere (key length = {}): {}\n..."
              .format(self.key_length, text))
        for guess in guesses:
            decryption, score, key = guess
            print("score: {} - key: {} - plaintext: {}"
                  .format(score, key, decryption))
        print("")

    def guess(self, text):
        ciphertext_chunks = self.chunk(text)
        plaintext_chunks, keys = self.break_caesars(ciphertext_chunks)
        plaintext = self.zip(plaintext_chunks)
        return [(plaintext, None, "".join(keys))]

    def chunk(self, text):
        chunks = {key: [] for key in range(self.key_length)}
        for i in range(len(text)):
            chunks[i % self.key_length].append(text[i])
        return ["".join(chunk) for _, chunk in chunks.items()]

    def break_caesars(self, chunks):
        plaintexts, keys = [], []
        for chunk in chunks:
            plaintext, score, key = self.caesar_breaker.guess(chunk, 1)[0]
            plaintexts.append(plaintext)
            keys.append(key)
        return plaintexts, keys

    def zip(self, chunks):
        result = []
        max_lenght = max([len(chunk) for chunk in chunks])
        for i in range(max_lenght):
            for chunk in chunks:
                if i < len(chunk):
                    result.append(chunk[i])
        return "".join(result)


class KeylengthDetector(object):
    def __init__(self, scorer, min_keylength=1, max_keylength=20,
                 expected_score_plaintext=0.06, verbose=True):
        self.scorer = scorer
        self.min_n = min_keylength
        self.max_n = max_keylength
        self.expected_score_plaintext = expected_score_plaintext
        self.expected_score_random = 0.035
        assert self.expected_score_plaintext > self.expected_score_random, \
            "The expected score for plaintext must be larger than for " \
            "random strings!"
        self.threshold = (self.expected_score_plaintext +
                          self.expected_score_random) / 2
        self.verbose = verbose

    def detect(self, text):
        scores = {i: self.score(text, i)
                  for i in range(self.min_n, self.max_n+1)}
        scores = OrderedDict(sorted(scores.items(), reverse=True,
                                    key=lambda t: t[1]))
        if self.verbose:
            self.validate_heuristically(scores)
        return scores

    def validate_heuristically(self, scores):
        print("Validating scores heuristically...")
        print("Splitting into high and low value groups...")
        max_score, min_score = max(scores.values()), min(scores.values())
        if max_score < self.threshold:
            print("WARNING: Highest score too low... " +
                  "probably no key length will work!!!")
        if min_score > self.threshold:
            print("WARNING: Lowest score too high... " +
                  "is the text already plaintext???")
        high_scores, low_scores = {}, {}
        for key, score in scores.items():
            if abs(score - max_score) < abs(score - min_score):
                high_scores[key] = score
            else:
                low_scores[key] = score
        print("Eliminating duplicates in high value group...")
        result = {}
        for key, score in high_scores.items():
            if (key % 2 != 0) or (key / 2 not in high_scores.keys()):
                result[key] = score
        print("Candidate key length values are:")
        for key, score in result.items():
            print("{}: {}".format(key, score))
        return None

    def chunk(self, text, n):
        chunks = {key: [] for key in range(n)}
        for i in range(len(text)):
            chunks[i % n].append(text[i])
        return ["".join(chunk) for _, chunk in chunks.items()]

    def score(self, text, n):
        chunks = self.chunk(text, n)
        return sum([self.scorer.score(chunk) for chunk in chunks]) / n

if __name__ == "__main__":
    import sys
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "..", ".."))
    from cryptanalysis.util.transforms import Masker
    from cryptanalysis.score.ioc import IocScorer
    from cryptanalysis.data.en import load_ngrams
    from cryptanalysis.score.ngram import NgramScorer

    text1, masker1 = Masker.from_text("vptnvffuntshtarptymjwzirappljmhhqvsubwlzzygvtyitarptyiougxiuydtgzhhvvmumshwkzgstfmekvmpkswdgbilvjljmglmjfqwioiivknulvvfemioiemojtywdsajtwmtcgluysdsumfbieugmvalvxkjduetukatymvkqzhvqvgvptytjwwldyeevquhlulwpkt")
    text2, masker2 = Masker.from_text("THEREARETWOWAYSOFCONSTRUCTINGASOFTWAREDESIGNONEWAYISTOMAKEITSOSIMPLETHATTHEREAREOBVIOUSLYNODEFICIENCIESANDTHEOTHERWAYISTOMAKEITSOCOMPLICATEDTHATTHEREARENOOBVIOUSDEFICIENCIESTHEFIRSTMETHODISFARMOREDIFFICULT")

    # Key length detection
    s = IocScorer(alphabet_size=26)
    print("Detecting for text 1 - true key length is 7")
    KeylengthDetector(s).detect(text1)
    print("")
    print("Detecting for text 1 - true key length is 7 but we only test up to 6 - should print warning")
    KeylengthDetector(s, max_keylength=6).detect(text1)
    print("")
    print("Detecting for text 2 - plain english, prints a warning")
    KeylengthDetector(s).detect(text2)

    # Viginere breaking
    print("Breaking cipher of text1: keylength is 7")
    scorer = NgramScorer(load_ngrams(1))
    breaker = VigenereBreak(7, scorer)
    breaker.analyse(text1)
