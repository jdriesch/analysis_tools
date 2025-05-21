import ROOT

from src.base_correction import BaseCorrection


wfile = 'src/bosonpt/weights.root'
ROOT.gROOT.ProcessLine(f'TFile* tf = TFile::Open("{wfile}", "read");')
ROOT.gROOT.ProcessLine('TH1D* h_weight = (TH1D*) tf->Get("pt_visweight");')


class BosonPtCorrection(BaseCorrection):
    """
    Class to apply the boson pT correction.
    """

    def run(self):
        """
        Run the correction.
        """
        
        arguments = self.infiles
        self.logger.info(
            f"Applying boson pT correction to {len(arguments)} files with "\
            f"{self.nthreads} cores."
        )
        self.run_multicore(arguments, self.nthreads)
        self.logger.info("Finished applying boson pT correction.")


    def job_wrapper(self, args):
        return self.execute(args)
    

    def execute(self, f_in):
        """
        Apply pileup correction to the input file.
        """

        # check if file is a zombie file
        f_out = self.check_file(f_in)
        if not f_out:
            return

        # load dataframe
        rdf = ROOT.RDataFrame('ntuple', f_in)
    
        # check if signal
        is_sigw = ("/WtoLNu" in f_in and "mmet" in f_in)
        is_sigdy = ("DYto2L" in f_in and "/mm/" in f_in)


        if is_sigdy:
            rdf = rdf.Define(
                "ptweight",
                "h_weight->GetBinContent(h_weight->FindBin(pt_vis))"
            )
        elif is_sigw:
            rdf = rdf.Define(
                "ptweight",
                "h_weight->GetBinContent(h_weight->FindBin(genbosonpt))"
            )
        else:
            rdf = rdf.Define("ptweight", "1.0")

        # variations
        rdf = rdf.Define("ptweightUp", "2*ptweight - 1.0")
        rdf = rdf.Define("ptweightDn", "1.0")
        
        # prepare saving
        quants = ["ptweight", "ptweightUp", "ptweightDn"]

        rdf.Snapshot("ntuple", f_out, quants)

        return


    def normalize(df, weight):
        """
        Normalize the weight to 1. Currently not used.
        """
        mean = df.Mean(weight).GetValue()
        df = df.Redefine(weight, f"{weight}/{mean}")
        return df
