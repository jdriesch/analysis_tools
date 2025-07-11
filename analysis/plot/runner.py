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
        fillcolor=ROOT.kBlue,
        linewidth=3,
    )
    plotter.add_process(
        name='EWK',
        subprocesses=['VV', 'ST', 'DYnonfid', 'DYtau', 'VBF'],
        linecolor=ROOT.kBlack,
        fillcolor=ROOT.kGreen-8,
        linewidth=3,
    )
    plotter.add_process(
        name='TT',
        subprocesses=['TT'],
        linecolor=ROOT.kBlack,
        fillcolor=ROOT.kMagenta+3,
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
        processes=['DY', 'EWK', 'TT'],
        draw_opt='HIST',
    )

    # Load the histograms
    plotter.add_histogram(
        name='m_vis_corr',
        variations=['_Nominal'],
        xtitle='m_{vis} (GeV)',
        ytitle='Events',
        xrange=[60, 120],
        yrange=[0, 1e6],
        ratiorange=[0.9, 1.1],
        legend_pos=(0.65, 0.5, 0.9, 0.9),
        draw_order=['Sim', 'Data']
    )

    plotter.construct_all_hists()
    plotter.execute_all()