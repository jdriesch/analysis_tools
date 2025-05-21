import ROOT

class HistogramHandler:
    def __init__(self, histo):
        self.histo = histo

    def make_histogram(self):
        return self.histo

    def set_histogram(self, histo):
        self.histo = histo

    def get_integral(self):
        return self.histo.Integral()

    def get_mean(self):
        return self.histo.GetMean()

    def get_std_dev(self):
        return self.histo.GetStdDev()

    def get_entries(self):
        return self.histo.GetEntries()