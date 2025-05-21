import ROOT
from glob import glob
import sys


class HistMaker:
    """
    Class to setup rdf for specific process w/ baseselection.
    Then, different additional selections can be applied and the histograms built.
    """

    def __init__(
        self, files, friends = [], 
        definitions={}, 
        base_selection={}, process_selection={}, add_selection={},
        nthreads=1
    ):
        """
        Initialize the histogram class.
        """

        self.files = files
        self.friends = friends
        self.definitions = definitions
        self.base_selection = base_selection
        self.process_selection = process_selection
        self.add_selection = add_selection
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
        Load the dataframe from the ROOT files.
        """
        # initialize main chain and friend chains
        chain = ROOT.TChain('ntuple')
        ch_friends = {}
        for friend in self.friends:
            ch_friends[friend] = ROOT.TChain('ntuple')

        # add files to corresponding friend chains
        for file in self.files:
            chain.Add(file)
            for friend in self.friends:
                f_friend = file.replace("ntuples", f"friends/{friend}")
                ch_friends[friend].Add(f_friend)
        
        # add friend chains to main chain
        for friend in self.friends:
            chain.AddFriend(ch_friends[friend])
        
        self.chain = chain
        
        return


    def create_df(self):
        """
        Create a dataframe from the ROOT TChain.
        """
        # create rdf without selections
        rdf = ROOT.RDataFrame(self.chain)

        # defining variables necessary for filtering/plotting
        for var, expr in self.definitions.items():
            rdf = rdf.Define(var, expr)

        # perform baseselection for the corresponding signal region
        for sel, expr in self.base_selection.items():
            rdf = rdf.Filter(expr)
        
        # perform process selection for corresponding process
        for filter in self.process_selection:
            rdf = rdf.Filter(filter)

        self.rdf = rdf

        return
    

    def make_hists(self, hists):
        """
        Create histograms from the dataframe.
        hists = {}
        """

        rdf = self.rdf

        # final selections that are histogram-specific
        for sel, expr in self.add_selection.items():
            rdf = rdf.Filter(expr)

        # create the cpp objects for the histograms
        for hist in hists:
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
    

if __name__=='__main__':
    # for batch submission or local usage
    args = sys.argv[]
    init_args = args[1:-2]
    proc = ProcessManager(*init_args)
    proc.make_hists(args[-2])
    proc.save_hists(args[-1])