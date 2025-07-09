#from winreg import HKEY_DYN_DATA
import ROOT
import os,sys
import numpy as np
from glob import glob

ROOT.gROOT.SetBatch(True)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)
ROOT.RooMsgService.instance().setSilentMode(True)
ROOT.gROOT.ProcessLine("RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);")
ROOT.gROOT.ProcessLine("RooMsgService::instance().setSilentMode(true);")


def fit_pol(graph, fdict, isoSR):
    """
    Fit a given function to a graph.
    """

    func = fdict["func"]
    lcol = fdict["lcol"]

    # fit range
    fitmin = 0.20  # 0.25
    fitmax = 1.00  # 0.60
    graph.Fit(func, "R0", "", fitmin, fitmax)

    val = func.GetParameter(0)
    err = func.GetParError(0)

    func.SetLineStyle(2)
    func.SetLineWidth(3)
    func.SetLineColor(lcol)

    graph_extr = ROOT.TGraphErrors(1, np.array([isoSR]), np.array([val]), np.zeros(1), np.array([abs(err)]))
    graph_extr.SetMarkerColor(lcol)
    graph_extr.SetMarkerStyle(47)
    graph_extr.SetMarkerSize(2)

    return func, graph_extr, val, err



def ExpltOneBin(isocenters, bincontents, binerrors, isoSR, suffix=""):
    """
    extrapolate the QCD shape from a set of control regions (isocenters)
    to the signal region (isoSR), using linear extrapolation
    and the 2nd order polynomial function
    """
    graph = ROOT.TGraphErrors(
        len(bincontents),
        np.array(isocenters), np.array(bincontents),
        np.zeros(len(bincontents)), np.array(binerrors)
    )
    graph.SetMarkerStyle(20)

    # pol1 and pol2
    functions = {
        "pol1": {
            "func": ROOT.TF1(
                "pol1_"+suffix,
                f"[1]*(x-{isoSR})+[0]", -0.1, 1.0
            ),
            "lcol": 46
        },
        "pol2": {
            "func": ROOT.TF1(
                "pol2_"+suffix,
                f"[2]*(x-{isoSR})*(x-{isoSR})+[1]*(x-{isoSR})+[0]", -0.1, 1.0
            ),
            "lcol": 9
        }
    }

    hists_tosave = [graph]
    results = {}

    for key in functions:
        func, graph_extr, val, err = fit_pol(graph, functions[key], isoSR)
        hists_tosave += [func, graph_extr]
        results[key] = (val, err)

    # TODO save histograms

    return results


def construct_qcd(isobin, region, mcscale=1):
    """
    collect both data and simulation histograms and 
    construct qcd template by subtracting sim from the data.
    The signal contamination can be varied with mcscale.
    """
    # collect all files from the isobins
    rfiles = f"output/batch_jobs/{region}/{isobin}/*.root"
    all_files = glob(rfiles)

    # construct histogram from data
    rfile = f"output/batch_jobs/{region}/{isobin}/Data_Data.root"
    tfile = ROOT.TFile(rfile, 'read')
    hist = tfile.Get('pfmt_corrNominal').Clone()
    hist.SetDirectory(ROOT.nullptr)
    tfile.Close()

    # subtract all simulation histograms in this bin
    for f in all_files:

        if 'Data' in f:
            continue

        tfile = ROOT.TFile(f, 'read')
        hist_f = tfile.Get('pfmt_corrNominal').Clone()

        # signal contamination variation
        if f'{region}_{region}' in f:
            hist_f.Scale(mcscale)

        hist.Add(hist_f, -1)
        tfile.Close()

    for bin in range(hist.GetNbinsX()):
        if hist.GetBinContent(bin) < 0:
            hist.SetBinContent(bin, 0)

    # scale to the same value for each isolation region
    hist.Scale(1./hist.Integral())

    return hist



def extrapolate_all(region, mcscale, save_dir, save_option):
    """
    obtain the different qcd extrapolations.
    """
    isoSR = [
        0.0662, 0.0645, 0.0616, 0.0578,
        0.0533, 0.0488, 0.0442, 0.0402, 
        0.0367, 0.0338, 0.0317, 0.0301, 
        0.029, 0.0281, 0.0274, 0.0272, 
        0.0271, 0.0272, 0.0281, 0.031
    ]

    if mcscale > 1:
        suffix = '_mcscaleUp'
    elif mcscale < 1:
        suffix = '_mcscaleDown'
    else:
        suffix = ''

    h_nom = ROOT.TH1F(
        f'pfmt_corr{suffix}', '',
        20, 0, 120
    )

    isocuts = [round(i, 3) for i in np.arange(0.2, 1.0, 0.05)]
    isocenters = [(isocuts[i]+isocuts[i+1])/2 for i in range(len(isocuts)-1)]

    isobins = [f"iso_bin_{i}" for i in range(5, 21)]

    # get the qcd estimations in different iso bins
    qcd_hists = {}
    for isobin in isobins:
        qcd_hists[isobin] = construct_qcd(isobin, region, mcscale)

    # get the qcd estimations
    h_up = []
    h_dn = []

    for mt in range(1, 21):

        # perform extrapolation
        binvalues = []
        binerrors = []
        for isobin in isobins:
            binvalues.append(qcd_hists[isobin].GetBinContent(mt))
            binerrors.append(qcd_hists[isobin].GetBinError(mt))

        results = ExpltOneBin(isocenters, binvalues, binerrors, isoSR[mt-1])

        pol1_val, pol1_err = results['pol1']
        pol2_val, pol2_err = results['pol2']

        # fill histograms
        # nominal
        h_nom.SetBinContent(mt, pol1_val)

        # variation of current mt bin
        syst = (pol1_err**2 + (pol1_val - pol2_val)**2)**0.5
        h_up.append(h_nom.Clone(f'pfmt_corr{suffix}_bin{mt}Up'))
        h_up[-1].SetBinContent(mt, pol1_val + syst)
        h_dn.append(h_nom.Clone(f'pfmt_corr{suffix}_bin{mt}Down'))
        h_dn[-1].SetBinContent(mt, pol1_val - syst)

        # remaining histogram bins
        for i in range(len(h_up)-1):
            h_up[i].SetBinContent(mt, pol1_val)
            h_dn[i].SetBinContent(mt, pol1_val)

    # save histograms
    tf = ROOT.TFile(save_dir, save_option)
    h_nom.Write()
    for h in h_up:
        h.Write()
    for h in h_dn:
        h.Write()
    tf.Close()

# TODO implement plots