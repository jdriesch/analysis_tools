import ROOT
import os
import correctionlib
correctionlib.register_pyroot_binding()

from src.base_correction import BaseCorrection


# adapted pog weight -> only for Run 2022C
ROOT.gROOT.ProcessLine(
    'TFile* f_pref = TFile::Open("src/pileup/npu_weight.root", "read");\
    TH1D* h_pu = (TH1D*)f_pref->Get("pileuphist");\
    TH1D* h_pu_up = (TH1D*)f_pref->Get("pileuphist_up");\
    TH1D* h_pu_dn = (TH1D*)f_pref->Get("pileuphist_dn");'
)

# central pog weight
pileup_name = 'Collisions2022_355100_357900_eraBCD_GoldenJson'
ROOT.gROOT.ProcessLine(
    f'auto cset = correction::CorrectionSet::from_file("src/pileup/puWeights.json");\
    auto cset_pu = cset->at("{pileup_name}");'
)

class PileupCorrection(BaseCorrection):


    def run(self):
        """
        Run the correction.
        """
        
        arguments = self.infiles
        self.logger.info(
            f"Applying pileup correction to {len(arguments)} files with "\
            f"{self.nthreads} cores."
        )
        self.run_multicore(arguments, self.nthreads)
        self.logger.info("Finished applying pileup correction.")


    def job_wrapper(self, args):
        return self.execute(args)


    def execute(self, f_in):
        """
        Apply pileup correction to the input file.
        """

        # check if file is a zombie file
        f_out = self.check_file(f_in)

        # load dataframe
        rdf = ROOT.RDataFrame('ntuple', f_in)

        # check if data
        is_data = (rdf.Sum("is_data").GetValue()>0)

        # check if W region
        mmet = False
        if '/mmet/' in f_out:
            mmet = True

        # apply weights
        vars_central = {'': 'nominal', 'Up': 'up', 'Dn': 'down'}
        vars_onlyc = {'': '', 'Up': '_up', 'Dn': '_dn'}

        for var in vars_central.keys():
            if is_data:
                rdf = rdf.Define(f"pog_puweight{var}_bcd", "1.")
                rdf = rdf.Define(f"pog_puweight{var}", "1.")
            
            else:
                rdf = rdf.Define(
                    f"pog_puweight{var}_bcd",
                    f'cset_pu->evaluate({{npu, "{vars_central[var]}"}})'
                )
                rdf = rdf.Define(
                    f"pog_puweight{var}",
                    f"h_pu->GetBinContent(h_pu{vars_onlyc[var]}->FindBin(npu))"
                )
            
                rdf = self.normalize(rdf, f"pog_puweight{var}_bcd", mmet)
                rdf = self.normalize(rdf, f"pog_puweight{var}", mmet)
        
        # save output
        quants = [
            "pog_puweight", "pog_puweightUp", "pog_puweightDn",
            "pog_puweight_bcd", "pog_puweightUp_bcd", "pog_puweightDn_bcd",
        ]
            
        rdf.Snapshot("ntuple", f_out, quants)



    def normalize(self, df, weight, mmet):
        """
        Normalize the weight to the sum of genweights.
        The correction should not change the overall yield in simulation.
        """
        # apply selections
        if mmet:
            rdf = df.Filter(
                    "pt_1 > 25"\
                    "&& tightId_1 && iso_1 < 0.15"\
                    "&& abs(eta_1) < 2.4"
            )
        else:
            rdf = df.Filter(
                    "pt_1 > 25 && pt_2 > 25 && q_1 * q_2 < 0"\
                    "&& tightId_1 && tightId_2 && iso_1 < 0.15 && iso_2 < 0.15"\
                    "&& m_vis > 60 && m_vis < 120"\
                    "&& abs(eta_1) < 2.4 && abs(eta_2) < 2.4"
            )

        # get sum of genweights
        rdf = rdf.Define("gensign", 'genweight > 0 ? 1 : (genweight < 0 ? -1 : 0.)')
        sum_genweights = rdf.Mean('gensign').GetValue()

        if sum_genweights > 0:
            rdf = rdf.Define(weight+'sign', f'{weight} * gensign')

            mean = rdf.Mean(weight+'sign').GetValue() / sum_genweights

            if (mean - 1) > 0.01:
                self.logger.warning(
                    f"Mean of {weight} is {mean}, and therefore"\
                    " and therefore far away from 1."\
                    " Please Consider checking the weight."
                )
            df = df.Redefine(weight, f"{weight}/{mean}")
        else:
            self.logger.warning(
                f"Sum of genweights is {sum_genweights}."\
                " Please consider checking the weight."
            )

        return df
