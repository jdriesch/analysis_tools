from src.base_correction import BaseCorrection

import ROOT
import json


class METXYCorrection(BaseCorrection):
    """
    Class to apply the XY correction.
    """

    def run(self):
        """
        Run the correction.
        """
        
        arguments = self.infiles
        self.logger.info(
            f"Applying XY correction to {len(arguments)} files with "\
            f"{self.nthreads} cores."
        )
        self.run_multicore(arguments, self.nthreads)
        self.logger.info("Finished applying XY correction.")

    
    def prepare(self):
        """
        Prepare the correction.
        """
        with open("src/metxy/corr.json", "r") as f:
            self.corr_dict = json.load(f)

        return
    

    def job_wrapper(self, args):
        return self.execute(args)
        

    def execute(self, f_in):
        """
        Apply XY correction to the input file.
        """

        # check if file is a zombie file
        f_out = self.check_file(f_in)
        if not f_out:
            return

        # load dataframe
        rdf = ROOT.RDataFrame('ntuple', f_in)

        # check if data
        is_data = (rdf.Sum("is_data").GetValue()>0)

        if is_data:
            ch = 'data'
        else:
            ch = 'mc'

        # construct x and y components
        rdf = rdf.Define(
            "pfmet_x",
            "pfmet_uncorrected * cos(pfmetphi_uncorrected)"
        )
        rdf = rdf.Define(
            "pfmet_y",
            "pfmet_uncorrected * sin(pfmetphi_uncorrected)"
        )

        # correct components
        rdf = rdf.Define(
            "pfmet_xycorr_x", 
            f"pfmet_x - (({self.corr_dict[ch+'_x']['m']}) * npvGood "\
            f"+ ({self.corr_dict[ch+'_x']['c']}))"
        )
        rdf = rdf.Define(
            "pfmet_xycorr_y",
            f"pfmet_y - (({self.corr_dict[ch+'_y']['m']}) * npvGood + "\
            f"({self.corr_dict[ch+'_y']['c']}))"
        )

        # construct xy corrected met from components
        rdf = rdf.Define(
            "pfmet_xycorr",
            "sqrt( pow(pfmet_xycorr_x, 2) + pow(pfmet_xycorr_y, 2) )"
        )
        rdf = rdf.Define(
            "pfmetphi_xycorr", "atan2(pfmet_xycorr_y, pfmet_xycorr_x)"
        )

        # prepare saving
        quants = ["pfmet_xycorr", "pfmetphi_xycorr"]

        rdf.Snapshot("ntuple", f_out, quants)

        return