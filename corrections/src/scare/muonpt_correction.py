from src.base_correction import BaseCorrection

import ROOT
import numpy as np


class MuonPtCorrection(BaseCorrection):
    """
    Class to apply the muon pT correction.
    """

    def run(self):
        """
        Run the correction.
        """
        
        arguments = self.infiles
        self.logger.info(
            f"Applying muon pT correction to {len(arguments)} files with "\
            f"{self.nthreads} cores."
        )
        self.run_multicore(arguments, self.nthreads)
        self.logger.info("Finished applying muon pT correction.")

    
    def job_wrapper(self, args):
        return self.execute(args)
    

    def prepare(self):
        """
        Prepare the correction.
        """
        ROOT.gInterpreter.Declare("""
            double gaus(){
                return gRandom->Gaus(0,1);
            }
        """)

        # load correction files
        self.res_sf = np.loadtxt('src/scare/correction_files/res_sf.txt')
        self.mz_mc = np.loadtxt('src/scare/correction_files/mc_response.txt')
        self.mz_dt = np.loadtxt('src/scare/correction_files/dt_response.txt')
        pt_sf = (91.1876+self.mz_mc) / (91.1876+self.mz_dt)
        self.mz_res_mc = np.loadtxt('src/scare/correction_files/mc_resolution.txt')
        self.mz_res_dt = np.loadtxt('src/scare/correction_files/dt_resolution.txt') * pt_sf

        # correction bins
        self.pt = [20, 30, 35, 39, 42, 45, 49, 60, 120, 9999]
        self.eta = [-2.4, -1.2, 0., 1.2, 2.4]
        self.vars = ['', '_up', '_dn', '_resolup', '_resoldn', '_scaleup', '_scaledn']

        return
    

    def calc_m(self, rdf, corr="", dilep=True):
        """
        function to calculate quantities of visible leptons
        
        (ROOT.RDataFrame) rdf: dataframe
        (str) corr: '' if uncorrected
        (bool) dilep: True if dilepton, False if single lepton
        """
        # construct visible four momentum
        if dilep:
            rdf = rdf.Define(
                f"lv_1{corr}", 
                f"ROOT::Math::PtEtaPhiMVector p(pt_1{corr}, eta_1, phi_1, mass_1);"\
                f"return p;"
                )
            rdf = rdf.Define(
                f"lv_2{corr}", 
                f"ROOT::Math::PtEtaPhiMVector p(pt_2{corr}, eta_2, phi_2, mass_2);"\
                f"return p;")
            rdf = rdf.Define(f"four_mom_vis{corr}", f"lv_1{corr} + lv_2{corr}")

        else:
            rdf = rdf.Define(
                f"lv_1{corr}", 
                f"ROOT::Math::PtEtaPhiMVector p(pt_1{corr}, eta_1, phi_1, mass_1);"\
                f"return p;"
                )
            rdf = rdf.Define(f"four_mom_vis{corr}", f"lv_1{corr}")

        rdf = rdf.Define(f"pt_vis{corr}", f"four_mom_vis{corr}.Pt()")
        rdf = rdf.Define(f"m_vis{corr}", f"four_mom_vis{corr}.M()")
        rdf = rdf.Define(f"phi_vis{corr}", f"four_mom_vis{corr}.Phi()")
        rdf = rdf.Define(f"rap_vis{corr}", f"four_mom_vis{corr}.Rapidity()")
        return rdf
    

    def correct_pt(self, rdf, i, j, k, is_data):
        """
        filter and apply corresponding corrections
        """
        # get bin edges
        eta_l, eta_r = self.eta[j], self.eta[j+1]
        pt_l, pt_r = self.pt[k], self.pt[k+1]

        # filter for a muon in event in corresponding bins
        filtera = f"(eta_{i} > {eta_l} && eta_{i} < {eta_r})"
        filterb = f"(pt_{i} > {pt_l} && pt_{i} < {pt_r})"
        
        # set resolution ratio to one if data resolution is larger
        if self.mz_res_mc[j][k] > self.mz_res_dt[j][k]:
            res_sf = 1
        else:
            res_sf = self.mz_res_dt[j][k] / self.mz_res_mc[j][k]

        # define momentum scale and resolution smearing
        mom_scale = f"(91.1876 + {self.mz_mc[j][k]}) /"\
                    f"(91.1876 + {self.mz_dt[j][k]})"
        res_smear = f"(1 + {self.res_sf[j][k]*self.mz_res_mc[j][k]} / "\
            f"91.1876 * sqrt( {res_sf**2}-1) * (double)(gaus()) )"

        # in data events: scale momentum to match peak position in mc
        if is_data:
            rdf = rdf.Redefine(
                f"pt_{i}_corr", 
                "double p;"\
                    f"if ({filtera} && {filterb}) p=pt_{i} * {mom_scale};"\
                    f"else p=pt_{i}_corr;"\
                    "return p;"
                )
            # update variations to post-correction values (fail save)
            for var in self.vars[1:]:
                rdf = rdf.Redefine(f'pt_{i}_corr{var}', f'pt_{i}_corr')

        # in mc events: smear pt to match mass resolution in data
        # furthermore, apply scale and resolution variations
        # the scale variations are applied reversely
        else:
            rdf = rdf.Redefine(
                f"pt_{i}_corr", 
                "double p;"\
                    f"if ({filtera} && {filterb}) p=pt_{i} * {res_smear};"\
                    f"else p=pt_{i}_corr;"\
                    "return p;"
                )
            rdf = rdf.Redefine(
                f"pt_{i}_corr_up",
                "double p;"\
                    f"if ({filtera} && {filterb})"\
                    f"p=pt_{i} * (1 + 1.5*({res_smear}-1) + 0.5*(1./({mom_scale})-1));"\
                    f"else p=pt_{i}_corr_up;"\
                    "return p;"
                )
            rdf = rdf.Redefine(
                f"pt_{i}_corr_scaleup",
                "double p;"\
                    f"if ({filtera} && {filterb})"\
                    f"p=pt_{i}_corr * (1 + 0.5*(1./({mom_scale})-1));"\
                    f"else p=pt_{i}_corr_scaleup;"\
                    "return p;"
                )
            rdf = rdf.Redefine(
                f"pt_{i}_corr_resolup",
                "double p;"\
                    f"if ({filtera} && {filterb})"\
                    f"p=pt_{i} * (1 + 1.5*({res_smear}-1));"\
                    f"else p=pt_{i}_corr_resolup;"\
                    "return p;"
                )
            rdf = rdf.Redefine(
                f"pt_{i}_corr_dn",
                "double p;"\
                    f"if ({filtera} && {filterb})"\
                    f"p=pt_{i} * (1 + 0.5*({res_smear}-1) - 0.5*(1./({mom_scale})-1));"\
                    f"else p=pt_{i}_corr_dn;"\
                    "return p;"
                )
            rdf = rdf.Redefine(
                f"pt_{i}_corr_scaledn",
                "double p;"\
                    f"if ({filtera} && {filterb})"\
                    f"p=pt_{i}_corr * (1 - 0.5*(1./({mom_scale})-1));"\
                    f"else p=pt_{i}_corr_scaledn;"\
                    "return p;"
                )
            rdf = rdf.Redefine(
                f"pt_{i}_corr_resoldn",
                "double p;"\
                    f"if ({filtera} && {filterb})"\
                    f"p=pt_{i} * (1 + 0.5*({res_smear}-1));"\
                    f"else p=pt_{i}_corr_resoldn;"\
                    "return p;"
                )
        return rdf


    def calc_recoil(self, rdf, is_dimuon, is_signal):
        """
        after having corrected the muon pT,
        the recoil needs to be corrected for this change
        """
         # set boson quantities to lepton stuff except for signal samples,
         # there use gen boson quantities
         # recoil not corrected for other samples anyway
        if not is_signal:
            bosonphi = "phi_vis_corr"
            bosonpt = "pt_vis_corr"
            bosonrap = "rap_vis_corr"
        else:
            bosonphi = "genbosonphi"
            bosonpt = "genbosonpt"
            bosonrap = "genbosonrapidity"

        rdf = rdf.Define("bosonpt", f"{bosonpt}")
        rdf = rdf.Define("bosonphi", f"{bosonphi}")
        rdf = rdf.Define("bosonrap", f"{bosonrap}")

        # define phi_vis (and pt_vis) for recoil correction
        if is_dimuon:        
            rdf = rdf.Define("pt_vis_x", "pt_1*cos(phi_1) + pt_2*cos(phi_2)")
            rdf = rdf.Define("pt_vis_y", "pt_1*sin(phi_1) + pt_2*sin(phi_2)")
            rdf = rdf.Define("phi_vis", "atan2(pt_vis_y, pt_vis_x)")
        else:
            rdf = rdf.Define("pt_vis", "pt_1")
            rdf = rdf.Define("phi_vis", "phi_1")

        # obtain recoil x and y components
        rdf = rdf.Define(
            "pfuPx",
            "pfmet_xycorr*cos(pfmetphi_xycorr) + pt_vis*cos(phi_vis)"
        ) 
        rdf = rdf.Define(
            "pfuPy",
            "pfmet_xycorr*sin(pfmetphi_xycorr) + pt_vis*sin(phi_vis)"
        )

        # obtain recoil components parallel and perpendicular to the boson
        rdf = rdf.Define(
            "pfuP1_uncorrected",
            f"- (pfuPx*cos({bosonphi}) + pfuPy*sin({bosonphi}))"
        )
        rdf = rdf.Define(
            "pfuP2_uncorrected",
            f"pfuPx*sin({bosonphi}) - pfuPy*cos({bosonphi})"
        )

        # corrected quantities:
        for var in self.vars:
            # first add again the corrected muon pT
            rdf = rdf.Define(
                f"pfmetx_lepcorr{var}",
                f"pfuPx - pt_vis_corr{var}*cos(phi_vis_corr{var})"
            )
            rdf = rdf.Define(
                f"pfmety_lepcorr{var}",
                f"pfuPy - pt_vis_corr{var}*sin(phi_vis_corr{var})"
            )
            
            # then calculate the met corrected for the muon pT
            rdf = rdf.Define(
                f"pfmet_lepcorr{var}",
                f"sqrt( pow( pfmetx_lepcorr{var} , 2 ) + pow( pfmety_lepcorr{var} , 2 ) )"
            )
            rdf = rdf.Define(
                f"pfmetphi_lepcorr{var}",
                f"atan2( pfmety_lepcorr{var} , pfmetx_lepcorr{var} )"
            )

        return rdf


    def execute(self, f_in):
        """
        Apply the muon pT correction to the input file.
        """

        # check if file is a zombie file
        f_out = self.check_file(f_in)
        if not f_out:
            return
        
        # prepare saving
        quants = []

        # load rdf
        chain = self.load_chains(f_in, ["metxy"])
        rdf = ROOT.RDataFrame(chain)

        # check if data
        is_data = (rdf.Sum("is_data").GetValue()>0)

        # check if W region
        is_dimuon = ("/mm/" in f_in)
        if is_dimuon:
            nums = [1, 2]
        else:
            nums = [1]

        # define initial values for correction
        for i in nums:
            for var in self.vars:
                rdf = rdf.Define(f"pt_{i}_corr{var}", f"pt_{i}")
    
            # go through all bins and apply corrections
            for j in range(len(self.eta)-1): 
                for k in range(len(self.pt)-1): 
                    rdf = self.correct_pt(rdf, i, j, k, is_data)

            quants += [f'pt_{i}_corr{var}']
            
        
        # calculate corrected visible mass, pt, phi, rap
        for var in self.vars:
            rdf = self.calc_m(rdf, '_corr'+var, dilep=is_dimuon)

            quants += [
                f'm_vis_corr{var}', f'pt_vis_corr{var}',
                f'phi_vis_corr{var}', f'rap_vis_corr{var}'
            ]

        # correct and add recoil variables
        is_signal = ("/WtoLNu" in f_in or "/DYto2L" in f_in)
        rdf = self.calc_recoil(rdf, is_dimuon, is_signal)
       
        met_cols = [
            "pfuP1_uncorrected", "pfuP2_uncorrected", 
            "bosonpt", "bosonphi", "bosonrap",
        ]
        for var in self.vars:
            met_cols += [f'pfmet_lepcorr{var}', f'pfmetphi_lepcorr{var}']

        # not_incl = [quant for quant in quants+met_cols if quant not in rdf.GetColumnNames()]

        rdf.Snapshot("ntuple", f_out, quants + met_cols)

        return