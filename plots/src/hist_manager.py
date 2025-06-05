import ROOT
from glob import glob

from src.hist_process import HistMaker
from plot_setup.variations import get_weights


import logging

# make all plots of different variations
# type 1: update the weight
# type 2: update the observable

logger = logging.getLogger(__name__)


class ProcessManager:
    """
    Class to manage different process classes.
    I.e., steer the class
    """

    def __init__(
        self, files, friends = [], 
        definitions={}, filters={},
        binnings={}, save_path='',
        categories=[],
        nthreads=1
    ):
        """
        Initialize the histogram class.
        """

        self.files = files
        self.friends = friends
        self.definitions = definitions
        self.base_selection = filters['base']
        self.process_selection = filters['process']
        self.add_selection = filters['add']
        self.hists = binnings
        self.histograms = []
        self.categories = categories
        self.save_path = save_path

        if nthreads > 1:
            ROOT.EnableImplicitMT(nthreads)

        for proc in self.files:
            if isinstance(proc, str):
                self.samples = glob(proc)
            else:
                self.files = proc

        return
    

    def run_local(self):
        """
        Collect all histograms and then save them to commong file.
        """
        save_opt = 'recreate'
        for i, cat in enumerate(self.categories):
            for proc in self.process_selection[cat]:
                weights = get_weights(proc)
                logger.info(f"Processing {proc} with {self.files[proc]}")

                # create the histogram class
                hist = HistMaker(
                    self.files, cat, proc, self.friends,
                    self.definitions, self.base_selection,
                    self.process_selection, self.add_selection,
                    weights,
                    nthreads=12
                )
                # run the histogram creation
                hist.make_hists(self.hists)
                hist.save_hists(
                    self.save_path, save_opt
                )

                save_opt = 'update'



    def run_batch(self):
        """
        Create the histograms in batch mode.
        """
        pass


    def run(self, local=True):
        """
        Run the histogram creation process.
        """
        if local:
            self.run_local()
        else:
            self.run_batch()