from pycipher import SimpleSubstitution
import random


class SubstitutionBreak(object):
    def __init__(self, scorer, seed=None):
        self.scorer = scorer
        self.candidates = []
        if seed is not None:
            random.seed(seed)

    def guess(self, text, n=3):
        assert len(self.candidates) >= n, \
            "You must optimize first to get at least {} candidates!"
        result = []
        for candidate in self.candidates[0:n]:
            key, score = candidate
            decryption = self.decipher(text, key)
            result.append((decryption, score, key))
        return result

    def optimise(self, text, n=20):
        for i in range(n):
            key, score = self.optimise_once(text)
            self.append_candidate(key, score)
            print("Iteration {}: key = {} | score = {} | plaintext = {}"
                  .format(i, key, score, self.decipher(text, key)[:30]))

    def append_candidate(self, key, score):
        self.candidates.append((key, score))
        self.candidates = sorted(self.candidates, reverse=True,
                                 key=lambda t: t[1])

    def optimise_once(self, text):
        key = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        random.shuffle(key)
        score = self.score_key(text, key)
        count = 0
        while count < 1000:
            new_key = self.random_swap(key)
            new_score = self.score_key(text, new_key)
            if new_score > score:
                key, score = new_key, new_score
                count = 0
            count = count+1
        return key, score

    def random_swap(self, key):
        a, b = random.randint(0, 25), random.randint(0, 25)
        new_key = list(key)
        new_key[a], new_key[b] = new_key[b], new_key[a]
        return "".join(new_key)

    def score_key(self, text, key):
        return self.scorer.score(self.decipher(text, key))

    def decipher(self, text, key):
        return SimpleSubstitution(key).decipher(text)


if __name__ == "__main__":
    import sys
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(dir_path, "..", ".."))
    from cryptanalysis.util.transforms import Masker
    from cryptanalysis.data.en import load_ngrams
    from cryptanalysis.score.ngram import NgramScorer

    ciphertext, masker = Masker.from_text('pmpafxaikkitprdsikcplifhwceigixkirradfeirdgkipgigudkcekiigpwrpucikceiginasikwduearrxiiqepcceindgmieinpwdfprduppcedoikiqiasafmfddfipfgmdafmfdteiki')
    scorer = NgramScorer(load_ngrams(4))
    breaker = SubstitutionBreak(scorer)
    print(breaker.optimise(ciphertext))
    # print(breaker.analyse(ciphertext))
