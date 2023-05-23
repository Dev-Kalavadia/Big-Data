from mrjob.job import MRJob
import re

WORD_RE = re.compile(r"[\w']+")

class MRWordCount(MRJob):
    def mapper(self, k, v):
        yield None, len(WORD_RE.findall(v))

    def reducer(self, k, vs):     
        yield "Total:", sum(vs)

if __name__ == '__main__':
    MRWordCount.run()