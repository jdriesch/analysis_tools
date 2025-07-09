import ROOT
from glob import glob
import sys
import logging
import json


logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # log to console
    ]
)
logger = logging.getLogger(__name__)


class HistMaker:
    """
    Class to setup rdf for specific process w/ baseselection.
    Then, different additional selections can be applied and the histograms built.
    """

    def __init__(
        self, files, cat, proc, friends = [], 
        definitions={}, 
        region_selection={}, process_selection={},
        weights={},
        nthreads=1
    ):
        """
        Initialize the histogram class.
        """

        logger.info(
            f"Initializing HistMaker for {proc} in category {cat}"\
            f" with files {files} and friends {friends}"
            f" and weights {weights}."
            f" Using {nthreads} threads."
        )

        self.files = files
        self.category = cat
        self.process = proc
        self.friends = friends
        self.weights = weights
        self.region_selection = region_selection
        self.process_selection = process_selection
        self.histograms = []
        self.definitions = definitions

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

        for var, expr in self.definitions.items():
            logger.debug(f"Defining {var} with {expr}")
            rdf = rdf.Define(var, expr)

        # perform selection for corresponding process
        for filter in self.process_selection:
            logger.debug(f"Filtering {filter}")
            rdf = rdf.Filter(filter)

        # perform selection for corresponding (signal) region
        for sel, expr in self.region_selection.items():
            rdf = rdf.Filter(expr)

        self.rdf = rdf

        logger.debug(
            f"Created dataframe for {self.process} with"
            f" entries: {rdf.Count().GetValue()}"
        )

        return
    

    def add_overflow(self, histo, nbins):
        """
        Add overflow to last bin
        """
        # get contents and uncertainties
        content_n = histo.GetBinContent(nbins)
        content_np1 = histo.GetBinContent(nbins+1)

        error_n = histo.GetBinError(nbins)
        error_np1 = histo.GetBinError(nbins+1)

        # apply calculation
        histo.SetBinContent(nbins, content_n + content_np1)
        histo.SetBinContent(nbins+1, 0)

        histo.SetBinError(nbins, (error_n**2 + error_np1**2)**.5)
        histo.SetBinError(nbins+1, 0)
        
        return histo


    def make_hists(self, hists):
        """
        Create histograms from the dataframe.
        hists = {}
        """

        rdf = self.rdf
        vars = rdf.GetColumnNames()
        logger.debug(f"Dataframe of process {self.process} has variables: {vars}")

        # create the cpp objects for the histograms
        for var in hists:
            for weight in self.weights:
                hist = hists[var]

                if weight+'_weight' not in vars:
                    logger.warning(
                        f"Variable {weight}_weight not found"
                        f" in dataframe for {self.process}"
                    )
                    continue
                if var not in vars and 'ntuple.'+var not in vars:
                    logger.warning(
                        f"Variable {var} not found in dataframe for {self.process}"
                    )
                    continue

                histo = rdf.Histo1D(
                    (
                        f'{var}_{weight}',
                        '',
                        hist['bins'][0],
                        hist['bins'][1],
                        hist['bins'][2]
                    ),
                    var,
                    weight+'_weight'
                ).Clone()

                if hist['overflow']:
                    logger.info('Adding overflow.')
                    histo = self.add_overflow(histo, hist['bins'][0])

                self.histograms.append(histo)
        
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
    options_file = args[1]
    proc = args[2]
    
    # load the options from the json file
    with open(options_file, 'r') as f:
        options = json.load(f)
    logger.info(f"Loaded options from {options_file} for process {proc}")

    # create the histogram maker
    option = options[int(proc)]
    if len(args) > 3:
        option['nthreads'] = int(args[3])


    hist = HistMaker(
        files=option['files'],
        cat=option['cat'],
        proc=proc,
        friends=option['friends'],
        definitions=option['definitions'],
        region_selection=option['region_selection'],
        process_selection=option['process_selection'],
        weights=option['weights'],
        nthreads=option['nthreads']
    )
    hist.make_hists(option['hists'])
    hist.save_hists(option['save_path'], 'recreate')