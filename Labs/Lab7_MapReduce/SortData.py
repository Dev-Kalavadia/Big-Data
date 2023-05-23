from mrjob.job import MRJob

class SortData(MRJob):

    def mapper(self, _, value):      
        yield str(value).zfill(10), ""

    def reducer(self, key, values):
        yield str(key), 1

if __name__ == '__main__':
     SortData.run()