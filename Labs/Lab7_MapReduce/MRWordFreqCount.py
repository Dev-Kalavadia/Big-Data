from mrjob.job import MRJob
import re

WORD_RE = re.compile(r"[\w']+")

class MRWordCount(MRJob):
    def mapper(self, k, v):
        for w in WORD_RE.findall(v):
            yield w, 1

    def reducer(self, k, vs):     
        yield k, sum(vs)   


if __name__ == '__main__':
    MRWordCount.run()