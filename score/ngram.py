from math import log10


class NgramScorer(object):
    def __init__(self, ngrams):
        self.ngrams = ngrams
        self._identify_ngram_length()
        self._calculate_log_probs()

    def _identify_ngram_length(self):
        lengths = {len(key) for key, value in self.ngrams.items()}
        assert len(lengths) == 1, "All ngrams must have the same length!"
        self.n = lengths.pop()

    def _calculate_log_probs(self, alpha=0.01):
        total = sum(value for key, value in self.ngrams.items())
        for key in self.ngrams.keys():
            self.ngrams[key] = log10(float(self.ngrams[key]) / total)
        self.alpha = log10(alpha / total)

    def score(self, text, split_by=None, ignore=''):
        if len(ignore) > 0:
            text = self._remove_characters(text, ignore)
        if split_by is not None:
            return sum(self._score(part) for part in text.split(split_by))
        else:
            return self._score(text)

    def _remove_characters(self, text, characters):
        for i in range(0, len(characters)):
            text = text.replace(characters[i:i+1], '')
        return text

    def _score(self, text):
        score = 0
        ngrams = self.ngrams.__getitem__
        for i in range(len(text) - self.n+1):
            current_token = text[i:i+self.n]
            if current_token in self.ngrams:
                score += ngrams(current_token)
            else:
                score += self.alpha
        return score
