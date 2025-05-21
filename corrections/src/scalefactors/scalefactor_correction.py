import ROOT
from collections import OrderedDict

from src.base_correction import BaseCorrection


class ScaleFactorCorrection(BaseCorrection):
    """
    Class to apply scale factors.
    """

    def prepare(self):
        # load the data files in ROOT
        ROOT.TH1.AddDirectory(ROOT.kFALSE)
        ROOT.TH2.AddDirectory(ROOT.kFALSE)
        ROOT.TH3.AddDirectory(ROOT.kFALSE)
        ROOT.gROOT.SetBatch(True)
        ROOT.gROOT.ProcessLine(
            'TFile* f_eff = TFile::Open("src/scalefactors/data/efficiencies_Oct23_zpt_pogpu.root");'
        )

        scalefactors = {
            "trk": "NUM_GlobalMuons_DEN_StandAlone_EraC_etasingle_pt",
            "sta": "NUM_StandAlone_DEN_genTracks_EraC_eta_pt",
            "id": "NUM_TightID_DEN_GlobalMuons_EraC_eta_pt",
            "iso": "NUM_PFIsoTight_DEN_TightID_EraC_eta_pt",
            "trg": "NUM_IsoMu24_DEN_TightID_and_PFIsoTight_EraC_charge_eta_pt",
        }

        highiso_bins = [0.2, 0.3, 0.5, 1.0]

        scalefactors_highiso = {
            "iso": "NUM_PFIso{}_DEN_TightID_EraC_etawide_ptwide",
            "trg": "NUM_IsoMu24_DEN_TightID_and_PFIso{}_EraC_charge_etawide_ptwide",
        }

        self.datamc = {
            "dt": "_efficiencyData",
            "mc": "_efficiencyMC",
            "sf": ""
        }

        self.sf_hists = {}

        # nominal scale factors
        for type, info in scalefactors.items():
            self.sf_hists[type] = {}
            for dtmc in self.datamc.keys():
                # old and new histogram names
                h_name_new = f"h_eff_{type}_{dtmc}"
                h_name_old = f"{info}{self.datamc[dtmc]}"
                if type == "trg":
                    ROOT.gROOT.ProcessLine(
                        f'TH3F* {h_name_new} = (TH3F*)f_eff->Get("{h_name_old}");'
                    )
                else:
                    ROOT.gROOT.ProcessLine(
                        f'TH2F* {h_name_new} = (TH2F*)f_eff->Get("{h_name_old}");'
                    )
                self.sf_hists[type][dtmc] = h_name_new

        # highiso scale factors
        for i in range(len(highiso_bins)-1):
            istr = str(highiso_bins[i]) + str(highiso_bins[i+1])
            istr = istr.replace('.', '')
            hname_old_trg = scalefactors_highiso["trg"].format(istr)
            hname_old_iso = scalefactors_highiso["iso"].format(istr)
            hname_new_trg = f"h_highiso_trg_{istr}"
            hname_new_iso = f"h_highiso_iso_{istr}"
            ROOT.gROOT.ProcessLine(
                f'TH3F* {hname_new_trg} = (TH3F*)f_eff->Get("{hname_old_trg}");'
            )
            ROOT.gROOT.ProcessLine(
                f'TH2F* {hname_new_iso} = (TH2F*)f_eff->Get("{hname_old_iso}");')

        ROOT.gROOT.ProcessLine('f_eff->Close();')

        # prefire file
        ROOT.gROOT.ProcessLine(
            'TFile* f_pref = TFile::Open("src/scalefactors/data/L1mu_prefiringvseta_2022C.root");'
        )
        ROOT.gROOT.ProcessLine(
            'TH1D* h_pref = (TH1D*)f_pref->Get("L1mu_prefvseta_num");'
        )
        ROOT.gROOT.ProcessLine(
            'TH1D* h_pref_den = (TH1D*)f_pref->Get("L1mu_prefvseta_den");'
        )
        ROOT.gROOT.ProcessLine('h_pref->Rebin(2);')
        ROOT.gROOT.ProcessLine('h_pref_den->Rebin(2);')
        ROOT.gROOT.ProcessLine('h_pref->Sumw2();')
        ROOT.gROOT.ProcessLine('h_pref->Divide(h_pref_den);')
        ROOT.gROOT.ProcessLine('f_pref->Close();')

        # define strings:
        self.pt_str = "TMath::Max("\
            "(float)(25. + 1.e-3), TMath::Min("\
            "(float)(120. - 1.e-3), (float)pt_{}))"

        self.eta_str = "TMath::Max("\
            "(float)(-2.4+ 1.e-3), TMath::Min("\
            "(float)(2.4 - 1.e-3), (float)eta_{}))"

        self.pref_str_nom = "h_pref->GetBinContent(h_pref->FindBin( (float)(eta_{}) ))"
        self.pref_str_err = "h_pref->GetBinError(h_pref->FindBin( (float)(eta_{}) ))"


        return 


    def job_wrapper(self, args):
        return self.execute(args)
    

    def run(self):
        """
        Run the correction.
        """
        
        arguments = self.infiles
        self.logger.info(
            f"Applying scale factor correction to {len(arguments)} files "\
            f"with {self.nthreads} cores."
        )
        self.run_multicore(arguments, self.nthreads)
        self.logger.info("Finished applying scale factor correction.")

        return
    
    
    def execute(self, f_in):
        """
        Apply scale factors to the input file.
        """

        # check if file is already there
        f_out = self.check_file(f_in)
        if not f_out:
            return
        
        # load data in dataframe
        rdf = ROOT.RDataFrame("ntuple", f_in)

        # check if one or two muons
        isdilepton = ("/mm/" in f_in)
        if isdilepton:
            nums = ["1", "2"]
        else:
            nums = ["1"]

        # prepare output columns
        out_columns = []

        # iterate over efficiencies for both data and MC and num muons
        # collect mc and data eff along with scale factors and errors
        for type, hname in self.sf_hists.items():
            for dtmc, eff in self.datamc.items():
                for num in nums:

                    if type == 'trg':
                        val_str = f"(float){hname[dtmc]}->GetBinContent(\
                            {hname[dtmc]}->GetXaxis()->FindBin(q_{num}),\
                            {hname[dtmc]}->GetYaxis()->FindBin({self.eta_str.format(num)}),\
                            {hname[dtmc]}->GetZaxis()->FindBin({self.pt_str.format(num)})\
                        )"

                    else:
                        val_str = f"(float){hname[dtmc]}->GetBinContent(\
                            {hname[dtmc]}->GetXaxis()->FindBin({self.eta_str.format(num)}),\
                            {hname[dtmc]}->GetYaxis()->FindBin({self.pt_str.format(num)})\
                        )"

                    val_name = f"val_{type}_{dtmc}_{num}"
                    err_name = f"err_{type}_{dtmc}_{num}"
                    err_str = val_str.replace("GetBinContent", "GetBinError")

                    rdf = rdf.Define(val_name, val_str)
                    rdf = rdf.Define(err_name, err_str)

                    rdf = rdf.Define(val_name+"_up", f"{val_name} + {err_name}")
                    rdf = rdf.Define(val_name+"_dn", f"{val_name} - {err_name}")
                    out_columns.append(val_name)
                    out_columns.append(val_name+"_up")
                    out_columns.append(val_name+"_dn")

            # calculate scale factors from efficiencies
            sf_name = f"sf_{type}"
            eff_mc_trg = f"(1. - (1. - val_{type}_mc_1)*(1. - val_{type}_mc_2))"

            for var in ['', '_up', '_dn']:

                if isdilepton:
                    # for two muons: combine the two scale factors
                    if type == "trg":
                        # trigger is special for two muons as combined unc is less likely
                        eff_dt_var = f"(1. - "\
                            f"(1. - (val_{type}_mc_1 * val_{type}_sf_1{var})) * "\
                            f"(1. - (val_{type}_mc_2 * val_{type}_sf_2{var})))"
                        rdf = rdf.Define(sf_name+var, f"(float)({eff_dt_var}/{eff_mc_trg})")
                    else:
                        # for other types: treat muons as correlated
                        rdf = rdf.Define(sf_name+var, f"(float)(val_{type}_sf_1{var})*(val_{type}_sf_2{var})")

                else:
                    # for one muon: use the scale factor directly
                    rdf = rdf.Define(sf_name+var, f"(float)(val_{type}_sf_1{var})")
                out_columns.append(sf_name+var)
                

        # prefiring: 0.9 to account for L1 -> HLT efficiency; unc. x1.2 to account for add. systematics
        pref_sf = f"(1 - 0.9 * {self.pref_str_nom.format(1)})"
        pref_sf_up = f"(1 - 0.9 * ({self.pref_str_nom.format(1)} - 1.2 * {self.pref_str_err.format(1)} ))"
        pref_sf_dn = f"(1 - 0.9 * ({self.pref_str_nom.format(1)} + 1.2 * {self.pref_str_err.format(1)} ))"

        if isdilepton:
            pref_sf += f"* (1 - 0.9 * {self.pref_str_nom.format(2)})"
            pref_sf_up += f"* (1 - 0.9 * ({self.pref_str_nom.format(2)} - 1.2 * {self.pref_str_err.format(2)}))"
            pref_sf_dn += f"* (1 - 0.9 * ({self.pref_str_nom.format(2)} + 1.2 * {self.pref_str_err.format(2)}))"

        rdf = rdf.Define("sf_prefire", pref_sf)
        rdf = rdf.Define("sf_prefire_up", pref_sf_up)
        rdf = rdf.Define("sf_prefire_dn", pref_sf_dn)
        
        out_columns.append("sf_prefire")
        out_columns.append("sf_prefire_up")
        out_columns.append("sf_prefire_dn")

        # highiso scalefactors only for W region, for QCD extraction
        if isdilepton:
            highiso_iso = "1"
            highiso_trg = "1"

        else:
            highiso_iso = f"Float_t sf = 1;\
                if (iso_1 > 0.2 && iso_1 < 0.3) sf = h_highiso_iso_0203->GetBinContent(\
                    h_highiso_iso_0203->GetXaxis()->FindBin({self.eta_str.format(1)}),\
                    h_highiso_iso_0203->GetYaxis()->FindBin({self.pt_str.format(1)}) );\
                else if (iso_1 > 0.3 && iso_1 < 0.5) sf = h_highiso_iso_0305->GetBinContent(\
                    h_highiso_iso_0305->GetXaxis()->FindBin({self.eta_str.format(1)}),\
                    h_highiso_iso_0305->GetYaxis()->FindBin({self.pt_str.format(1)}) );\
                else if (iso_1 > 0.5 && iso_1 < 1.0) sf = h_highiso_iso_0510->GetBinContent(\
                    h_highiso_iso_0510->GetXaxis()->FindBin({self.eta_str.format(1)}),\
                        h_highiso_iso_0510->GetYaxis()->FindBin({self.pt_str.format(1)}) );\
                return sf;\
            "
            highiso_trg = f'Float_t sf = 1;\
                if (iso_1 > 0.2 && iso_1 < 0.3) sf = h_highiso_trg_0203->GetBinContent(\
                    h_highiso_trg_0203->GetXaxis()->FindBin(q_1),\
                    h_highiso_trg_0203->GetYaxis()->FindBin({self.eta_str.format(1)}),\
                    h_highiso_trg_0203->GetZaxis()->FindBin({self.pt_str.format(1)}) );\
                if(sf==0) cout << iso_1 << " " << q_1 << " " << eta_1 << " " << pt_1 << endl;\
                else if (iso_1 > 0.3 && iso_1 < 0.5) sf = h_highiso_trg_0305->GetBinContent(\
                    h_highiso_trg_0305->GetXaxis()->FindBin(q_1),\
                    h_highiso_trg_0305->GetYaxis()->FindBin({self.eta_str.format(1)}),\
                    h_highiso_trg_0305->GetZaxis()->FindBin({self.pt_str.format(1)}) );\
                else if (iso_1 > 0.5 && iso_1 < 1.0) sf = h_highiso_trg_0510->GetBinContent(\
                    h_highiso_trg_0510->GetXaxis()->FindBin(q_1),\
                    h_highiso_trg_0510->GetYaxis()->FindBin({self.eta_str.format(1)}),\
                    h_highiso_trg_0510->GetZaxis()->FindBin({self.pt_str.format(1)}) );\
                return sf;\
            '
        
        rdf = rdf.Define("sf_highiso_iso", highiso_iso)
        rdf = rdf.Define("sf_highiso_trg", highiso_trg)

        rdf = rdf.Define("sf_highiso_iso_err", highiso_iso.replace('GetBinContent', 'GetBinError'))
        rdf = rdf.Define("sf_highiso_trg_err", highiso_trg.replace('GetBinContent', 'GetBinError'))

        rdf = rdf.Define("sf_highiso_iso_up", "sf_highiso_iso + sf_highiso_iso_err")
        rdf = rdf.Define("sf_highiso_iso_dn", "sf_highiso_iso - sf_highiso_iso_err")
        rdf = rdf.Define("sf_highiso_trg_up", "sf_highiso_trg + sf_highiso_trg_err")
        rdf = rdf.Define("sf_highiso_trg_dn", "sf_highiso_trg - sf_highiso_trg_err")

        out_columns += ["sf_highiso_iso", "sf_highiso_iso_up", "sf_highiso_iso_dn"]
        out_columns += ["sf_highiso_trg", "sf_highiso_trg_up", "sf_highiso_trg_dn"]

        rdf.Snapshot("ntuple", f_out, out_columns)
