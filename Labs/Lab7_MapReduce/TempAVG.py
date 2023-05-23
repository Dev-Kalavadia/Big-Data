from mrjob.job import MRJob

class MRAverageTemperatureByCity(MRJob):
    
    def mapper(self, _, line):
        city, temperature = line.split(',')
        yield city, float(temperature)
    
    def reducer(self, city, temperatures):
        temp = list(temperatures)
        yield city, sum(temp)/len(temp)

if __name__ == '__main__':
    MRAverageTemperatureByCity.run()
