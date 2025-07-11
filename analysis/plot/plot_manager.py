import matplotlib.pyplot as plt
import numpy as np
import ROOT

from .plot_distro import PlotDistro

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

class PlotManager():
    def __init__(self, loadpath, savepath):

        self.loadpath = loadpath
        self.savepath = savepath

    
    def add_process(
            self, name, subprocesses,
            linecolor=None, fillcolor=None, fillstyle=None,
            markerstyle=None, markersize=None, linewidth=None,
            draw_opt=None, legend_opt=None, hist_type='Sim'
        ):
        # Add a process to the plotter
        if not hasattr(self, 'processes'):
            self.processes = {}

        self.processes[name] = {
            'process': name,
            'subprocesses': subprocesses,
            'linecolor': linecolor,
            'fillcolor': fillcolor,
            'fillstyle': fillstyle,
            'markerstyle': markerstyle,
            'markersize': markersize,
            'linewidth': linewidth,
            'draw_opt': draw_opt,
            'legend_opt': legend_opt,
            'type': hist_type
        }


    def group_processes(self, group, processes, draw_opt):
        # Aggregate processes based on histogram type, e.g., 'Data', 'Sim'
        
        if not hasattr(self, 'process_groups'):
            self.process_groups = {}

        if group not in self.process_groups:
            self.process_groups[group] = {
                'processes': [],
                'draw_opt': draw_opt
            }
        else:
            print(f"Warning: Group '{group}' already exists. Overwriting.")

        for proc_name in processes:
            if proc_name not in self.processes:
                print(f"Warning: Process '{proc_name}' not found. Skipping.")
                continue
            else:
                self.process_groups[group]['processes'].append(self.processes[proc_name])

        return


    def add_histogram(
            self, name,
            xtitle=None, ytitle=None, ratiotitle=None,
            xrange=None, yrange=None, ratiorange=None,
            legend_pos=None,
            variations=['Nominal'],
            draw_order=['Sim', 'Data']
    ):
        # Add a histogram to the plotter
        if not hasattr(self, 'hists'):
            self.hists = []

        for variation in variations:

            self.hists.append({
                'name': name+variation,
                'xtitle': xtitle,
                'ytitle': ytitle,
                'ratiotitle': ratiotitle,
                'xrange': xrange,
                'yrange': yrange,
                'ratiorange': ratiorange,
                'legend_pos': legend_pos,
                'draw_order': draw_order,
            })


    def construct_all_hists(self):

        # Construct all histograms
        for hist in self.hists:
            hist['process_groups'] = self.process_groups


    
    def execute_single(self, index):
        # Execute a single plot
        single_plotter = PlotDistro(
            loadpath=self.loadpath,
            savepath=self.savepath,
            options=self.hists[index]
        )

        single_plotter.load_hists()
        single_plotter.draw_canvas()

        # Save the canvas
        single_plotter.save_canvas(self.savepath, self.hists[index]['name'])


    def execute_all(self):
        # Execute all histograms
        for i in range(len(self.hists)):
            self.execute_single(i)



if __name__ == "__main__":
    # Example usage

    loadpath = "test.root"
    savepath = "test.pdf"

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
        draw_opt='HIST same',
    )

    # Load the histograms
    plotter.add_histogram(
        name='m_vis',
        variations=['Nominal'],
        xtitle='m_{vis} (GeV)',
        ytitle='Events',
        xrange=[60, 120],
        yrange=[0, 1e6],
        ratio=[0.9, 1.1],
        legend_pos=(0.65, 0.5, 0.9, 0.9)
    )



    plotter.load_results()

    # Plot the histograms
    plotter.plot_results()

    plotter.plot_ratio()

    # Add the label
    plotter.plot_label()

    # Save the canvas
    plotter.draw_all()