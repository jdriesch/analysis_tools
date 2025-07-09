import ROOT
import re
import logging

logger = logging.getLogger(__name__)

class PrepareFit():
    """
    Class to prepare the fit for the analysis.
    Step 1: Collect the histograms from the different files.
    Step 2: Adjust the histogram normalization if applicable.
    Step 3: Save the histograms to a common file.
    """
    def __init__(self, varname, nuisances, region):
        """
        Initialize the class.
        """
        self.varname = varname
        self.nuisances = nuisances
        self.region = region

        self.histograms = {}


    def _align_name(self, hist, group):
        """
        Align histogram name with expected format in nuisances.
        """
        # remove Nominal from name
        hname = hist.GetName().replace('Nominal', '').strip('_')

        variation = re.sub(
            rf'{re.escape(self.varname)}_|up|dn|Up|Down',
            '',
            hname
        )

        # nominal histogram
        if variation == hname:
            logger.debug(
                f"Histogram {hname} is a nominal histogram. "
                f"Using it as is without variation."
            )
            return f'{group}_{hname}'

        # check if variation is in registered nuisances
        elif variation not in self.nuisances:
            logger.warning(
                f"Histogram {hname} with variation {variation} not "
                f"found in variations for region {self.region}. Skipping."
            )
            return False

        # prepare new name of histogram
        var_new = self.nuisances[variation]['name']

        hname_new = f'{group}_{hname.replace(variation, var_new)}'
        hname_new = hname_new.replace('up', 'Up').replace('dn', 'Down')

        return hname_new


    
    def register_histograms(self, files):
        """
        Load histograms from the given files.
        """
        for f in files:

            # get process group
            group = f.split('/')[-1].split('.')[0].split('_')[1]

            # get all histograms
            tfile = ROOT.TFile(f, 'read')

            for key in tfile.GetListOfKeys():

                hist = key.ReadObj()
                hist.SetDirectory(0)

                # align histogram name with nuisance name
                hname_new = self._align_name(hist, group)
                logger.debug(
                    f"Successfully collected histogram "
                    f"{hname_new} from file {f}."
                )

                if not hname_new:
                    continue

                elif hname_new in self.histograms:
                    self.histograms[hname_new].Add(hist)

                else:
                    self.histograms[hname_new] = hist

            tfile.Close()

        return


    def normalize_histograms(self):
        """
        Force the histograms to standard normalization if applicable.
        """ 

        for hname, hist in self.histograms.items():
            # check if histogram needs to be normalized
            var = hname.split('_')[-1].replace('Up', '').replace('Down', '')
            group = hname.split('_')[0]

            # skip nominal histograms
            if var not in self.nuisances:
                continue

            if self.nuisances[var]['normalize']:
                # get nominal normalization
                hist_nom = self.histograms[group + f'_{self.varname}']

                hist.Scale(hist_nom.Integral() / hist.Integral())

        return
    

    def save_histograms(self, save_path):
        """
        Save the histograms to a ROOT file.
        """
        tf = ROOT.TFile(save_path, 'RECREATE')
        if not tf.IsOpen():
            raise IOError(f"Could not open file {save_path} for writing.")

        for hist in self.histograms:
            self.histograms[hist].SetName(hist)
            self.histograms[hist].Write()

        tf.Close()
        logger.info(f"Histograms saved to {save_path}.")
        return