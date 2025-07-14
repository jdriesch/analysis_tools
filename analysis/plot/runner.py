import logging
import os
import ROOT

import config as cfg

from .plot_manager import PlotManager


logger = logging.getLogger(__name__)

def run_plotting(args):
    logger.info("Running the plotting mode.")

    # TODO: add variations

    region = 'Z'

    loadpath = f"output/{args.version}/batch_jobs/{region}/Nominal/"
    savepath = f"output/{args.version}/pdf/{region}/"

    os.makedirs(savepath, exist_ok=True)

    plotter = PlotManager(loadpath, savepath)
    
    # add different processes
    plotter.add_process(
        name='Data',
        subprocesses=['Data'],
        linecolor=ROOT.kBlack,
        markerstyle=20,
        markersize=1.2,
        linewidth=3,
        legend_opt='pex0 same',
        hist_type='Data'
    )
    plotter.add_process(
        name='DY',
        subprocesses=['DY'],
        linecolor=ROOT.kBlack,
        fillcolor=ROOT.kAzure+1,
        linewidth=3,
    )
    plotter.add_process(
        name='EWK',
        subprocesses=['VV', 'ST', 'DYnonfid', 'DYtau', 'VBF'],
        linecolor=ROOT.kBlack,
        fillcolor=ROOT.kGreen-9,
        linewidth=3,
    )
    plotter.add_process(
        name='TT',
        subprocesses=['TT'],
        linecolor=ROOT.kBlack,
        fillcolor=ROOT.kMagenta-8,
        linewidth=3,
    )

    # group processes
    plotter.group_processes(
        group='Data',
        processes=['Data'],
        draw_opt='pex0 ex0 same'
    )
    plotter.group_processes(
        group='Sim',
        processes=['TT', 'EWK', 'DY'],
        draw_opt='HIST',
    )

    # Load the histograms
    plotter.add_histogram(
        name='pfmet_corr',
        variations=['_Nominal'],
        xtitle='missing pt (GeV)',
        ytitle='Events',
        xrange=[60, 120],
        yrange=[1e2, 1e6],
        ratiorange=[0.7, 1.3],
        legend_pos=(0.75, 0.7, 0.9, 0.9),
        draw_order=['Sim', 'Data'],
        dolog=True,
        label='(CMS Data/Simulation)'
    )

    plotter.construct_all_hists()
    plotter.execute_all()
