import ROOT
from glob import glob
import sys
import logging

logger = logging.getLogger(__name__)


class HistMaker:
    """
    Class to setup rdf for specific process w/ baseselection.
    Then, different additional selections can be applied and the histograms built.
    """

    def __init__(
        self, files, cat, proc, friends = [], 
        definitions={}, 
        base_selection={}, process_selection={}, add_selection={},
        weights={},
        nthreads=1
    ):
        """
        Initialize the histogram class.
        """

        self.files = files[proc]
        self.category = cat
        self.process = proc
        self.friends = friends
        self.weights = weights
        self.base_selection = base_selection
        self.process_selection = process_selection[cat][proc]
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

        logger.debug(
            f"Loading files for {self.process} with"
            f" files {self.files}"
            f" and friends {self.friends}"
        )

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
        logger.debug('Creating RDataFrame for %s', self.process)
        rdf = ROOT.RDataFrame(self.chain)

        # defining variables necessary for filtering/plotting
        for var, expr in self.weights.items():
            logger.debug(f"Defining {var} with {expr}")
            rdf = rdf.Define(var+'_weight', expr)

        # perform baseselection for the corresponding signal region
        for sel, expr in self.base_selection.items():
            rdf = rdf.Filter(expr)
        
        # perform process selection for corresponding process
        for filter in self.process_selection:
            logger.debug(f"Filtering {filter}")
            rdf = rdf.Filter(filter)

        self.rdf = rdf

        logger.debug(
            f"Created dataframe for {self.process} with"
            f" entries: {rdf.Count().GetValue()}"
        )

        return
    

    def make_hists(self, hists):
        """
        Create histograms from the dataframe.
        hists = {}
        """

        rdf = self.rdf

        vars = rdf.GetColumnNames()

        # final selections that are histogram-specific
        for sel, expr in self.add_selection.items():
            rdf = rdf.Filter(expr)

        # create the cpp objects for the histograms
        for var in hists:
            for weight in self.weights:
                hist = hists[var]

                if weight+'_weight' not in vars or var not in vars:
                    logger.warning(
                        f"Variable {var} or weight {weight}_weight not found"
                        f" in dataframe for {self.process}"
                    )
                    continue

                self.histograms.append(
                    rdf.Histo1D(
                        (
                            self.process + var + weight,
                            '',
                            hist['bins'][0],
                            hist['bins'][1],
                            hist['bins'][2]
                        ),
                        var,
                        weight+'_weight'
                    )
                )
        
        return
    

    def save_hists(self, outpath, option="RECREATE"):
        """
        Save the histograms to a ROOT file.
        """
        logger.debug(f"Saving histograms to {outpath} with option {option}")
        tf = ROOT.TFile(outpath, option)

        for hist in self.histograms:
            hist.SetDirectory(ROOT.nullptr)
            tf.cd()
            hist.Write()

        tf.Close()
        self.histograms = []
        return
    

if __name__=='__main__':
    # for batch submission or local usage
    args = sys.argv
    print(args)
    files = args[1:-2]
    proc = HistMaker(files, args[-2])

    histo = {
        'm_vis': {
            'xtitle': 'p_{T} (GeV)',
            'ytitle': 'Events',
            'bins': [60, 60, 120],
            'weight': 'genweight'
        },
    }
    proc.make_hists(histo)

    root_file = args[-1]+'.root'
    print('Saving histograms to', root_file)
    proc.save_hists(root_file)