from collections import defaultdict


class IocScorer(object):
    def __init__(self, alphabet_size=26):
        self.alphabet_size = alphabet_size

    def score(self, text):
        # n different letters in alphabet
        # N is length of text
        # F_i frequency of i'th letter in text
        # (1 / (N (N-1))) + sum_i_1_n [ F_i (F_i - 1) ]
        hist = self._get_letter_frequencies(text)
        statistic = sum([value * (value - 1) for _, value in hist.items()])
        normalizing_factor = len(text) * (len(text) - 1)
        return statistic / normalizing_factor

    def _get_letter_frequencies(self, text):
        hist = defaultdict(lambda: 0)
        for char in list(text):
            hist[char] += 1
        return dict(hist)


if __name__ == "__main__":
    scorer = IocScorer(alphabet_size=26)

    text = "THEREARETWOWAYSOFCONSTRUCTINGASOFTWAREDESIGNONEWAYISTOMAKEITSOSIMPLETHATTHEREAREOBVIOUSLYNODEFICIENCIESANDTHEOTHERWAYISTOMAKEITSOCOMPLICATEDTHATTHEREARENOOBVIOUSDEFICIENCIESTHEFIRSTMETHODISFARMOREDIFFICULT"
    print("Score of sample english text is {}".format(scorer.score(text)))
    assert abs(scorer.score(text) - 0.068101) < 0.000001, "Error: Wrong result"
