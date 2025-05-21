import ROOT
from glob import glob


class HistManager:
    """
    Class to manage different process classes.
    I.e., steer the class
    """

    def __init__(
        self, files, friends = [], 
        definitions={}, filters=[], nthreads=1
    ):
        """
        Initialize the histogram class.
        """

        self.files = files
        self.friends = friends
        self.definitions = definitions
        self.filters = filters
        self.histograms = []

        if nthreads > 1:
            ROOT.EnableImplicitMT(nthreads)

        for proc in self.files:
            if isinstance(proc, str):
                self.samples = glob(proc)
            else:
                self.files = proc
        self.load_chain()
        self.create_df()

        return


    def load_chain(self):
        """
        Load the dataframe from the ROOT file.
        """
        chain = ROOT.TChain('ntuple')
        ch_friends = {}
        for friend in self.friends:
            ch_friends[friend] = ROOT.TChain('ntuple')

        for file in self.files:
            chain.Add(file)
            for friend in self.friends:
                f_friend = file.replace("ntuples", f"friends/{friend}")
                ch_friends[friend].Add(f_friend)
        
        for friend in self.friends:
            chain.AddFriend(ch_friends[friend])
        
        self.chain = chain
        
        return


    def create_df(self):
        """
        Create a dataframe from the ROOT TChain.
        """

        rdf = ROOT.RDataFrame(self.chain)

        for var, expr in self.definitions.items():
            rdf = rdf.Define(var, expr)

        for filter in self.filters:
            rdf = rdf.Filter(filter)
        
        self.rdf = rdf

        return
    

    def make_hists(self, hists):
        """
        Create histograms from the dataframe.
        hists = {}
        """

        for hist in hists:
            rdf = self.rdf
            for filter in hist['filters']:
                rdf = rdf.Filter(filter)

            self.histograms.append(
                rdf.Histo1D(
                    (
                        hist['name'],
                        hist['title'],
                        hist['bins'],
                        hist['xmin'],
                        hist['xmax']
                    ),
                    hist['var'],
                    hist['weight']
                )
            )
        
        return
    

    def save_hists(self, outpath, option="RECREATE"):
        """
        Save the histograms to a ROOT file.
        """

        tf = ROOT.TFile(outpath, option)
        for hist in self.histograms:
            hist.Write()
        tf.Close()
        self.histograms = []
        return