import ROOT
import logging

logger = logging.getLogger(__name__)


ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)


class PlotDistro:
    def __init__(self, loadpath, savepath, options):
        self.loadpath = loadpath
        self.savepath = savepath
        self.options = options
        self.hists = []
        self.ratio_hists = []
        self.drawn_objects = []
        self.stack_collection = []

        self.nratio = True # hard-coded for now

        self.load_hists()


    def get_process(self, proc):
        """
        Add subprocesses, e.g. 'EWK' consisting of ST, VV,...
        """
        # Load subprocesses from the options
        process = proc['process']
        subprocesses = proc['subprocesses']

        hist = False

        for i, subprocess in enumerate(subprocesses):
            rfile = f'{self.loadpath}/{subprocess}_{process}.root'
            tfile = ROOT.TFile.Open(rfile)

            h = tfile.Get(self.options['name']).Clone(process)
            h.SetDirectory(ROOT.nullptr)

            if not hist:
                hist = h
            else:
                hist.Add(h)

            tfile.Close()

        # Set histogram properties
        hist = self.set_properties(hist, proc)

        return hist


    def construct_group(self, group):
        """
        Construct the groups of processes: 'Data', 'Sim'
        """
        stack = ROOT.THStack(group, '')

        processes = self.options['process_groups'][group]['processes']

        for proc in processes:

            # Get the sum of histograms of the subprocesses (EWK = ST + VV + ...)
            hist = self.get_process(proc)
            self.hists.append(hist)
            stack.Add(hist)

        # avoid garbage collection
        self.stack_collection.append(stack)

        return stack


    def load_hists(self):
        self.stacks = {}

        for group in self.options['process_groups']:
            # Construct the group of processes (Data / Sim)
            self.stacks[group] = {
                'stack': self.construct_group(group),
                'draw_opt': self.options['process_groups'][group]['draw_opt'],
            }

        return


    def set_properties(self, hist, options):
        # Set the histogram properties

        if 'linecolor' in options and options['linecolor'] is not None:
            hist.SetLineColor(options['linecolor'])

        if 'linestyle' in options and options['linestyle'] is not None:
            hist.SetLineStyle(options['linestyle'])

        if 'fillcolor' in options and options['fillcolor'] is not None:
            hist.SetFillColor(options['fillcolor'])

        if 'fillstyle' in options and options['fillstyle'] is not None:
            hist.SetFillStyle(options['fillstyle'])

        if 'markerstyle' in options and options['markerstyle'] is not None:
            hist.SetMarkerStyle(options['markerstyle'])

        if 'markersize' in options and options['markersize'] is not None:
            hist.SetMarkerSize(options['markersize'])

        if 'linewidths' in options and options['linewidths'] is not None:
            hist.SetLineWidth(options['linewidths'])

        if 'xtitle' in options and options['xtitle'] is not None:
            hist.GetXaxis().SetTitle(options['xtitle'])

        if 'ytitle' in options and options['ytitle'] is not None:
            hist.GetYaxis().SetTitle(options['ytitle'])
 
        hist.SetTitle('')

        # axes
        xaxis = hist.GetXaxis()
        xaxis.SetTickLength(0.03)

        if 'xrange' in options:
            xaxis.SetRangeUser(options['xrange'][0], options['xrange'][1])

        return hist


    def setup_ratio(self, num, den):
        self.ratio_pad.cd()

        hist_num = self.stacks[num]['stack'].GetStack().Last().Clone(num + "_ratio")
        hist_den = self.stacks[den]['stack'].GetStack().Last().Clone(den + "_ratio")

        hist_num.Divide(hist_den)

        hist_num.Draw(self.stacks[num]['draw_opt'])

        self.ratio_hists.append(hist_num)

        # draw line
        line = ROOT.TLine(
            self.options['xrange'][0], 1, 
            self.options['xrange'][1], 1
        )
        line.SetLineColor(ROOT.kBlack)
        line.Draw("same")
        print(line)

        self.ratio_pad.Modified()
        self.ratio_pad.Update()

        self.canvas.Modified()
        self.canvas.Update()

        return

    def setup_pad(self):
        # Create a main pad and a ratio pad
        if self.nratio:
            self.main_pad = ROOT.TPad("main_pad", "main_pad", 0, 0.35, 1, 1)
            self.main_pad.Draw()
            self.main_pad.SetBottomMargin(0.025)
            self.main_pad.SetRightMargin(0.05)
            self.main_pad.SetLeftMargin(0.15)

            # ratio pad
            self.ratio_pad = ROOT.TPad("ratio_pad", "ratio_pad", 0, 0, 1, 0.35)
            self.ratio_pad.Draw()
            self.ratio_pad.SetTopMargin(0.05)
            self.ratio_pad.SetBottomMargin(0.35)
            self.ratio_pad.SetRightMargin(0.05)
            self.ratio_pad.SetLeftMargin(0.15)

            self.main_pad.cd()

        else:
            # self.main_pad = ROOT.TPad("main_pad", "main_pad", 0, 0, 1, 1)
            # self.main_pad.cd()
            self.canvas.cd()


    def plot_results(self):
        """
        plot results into the main pad
        """

        self.main_pad.cd()

        # respect draw order if provided
        if 'draw_order' in self.options:

            for group in self.options['draw_order']:

                if group not in self.stacks:
                    logger.warning(f"Group '{group}' not found in stacks.")
                    continue

                # Draw the stack for the group
                self.stacks[group]['stack'].Draw(
                    self.stacks[group]['draw_opt']
                )

        else:
            for group in self.stacks:
                self.stacks[group]['stack'].Draw(
                    self.stacks[group]['draw_opt']
                )

        self.canvas.Modified()
        self.canvas.Update()

        return


    def improve_visualization(self):

        self.main_pad.SetLogy(self.options['dolog'])

        for group in self.stacks:
            stack = self.stacks[group]['stack']
            if self.nratio:
                yaxis = stack.GetYaxis()
                yaxis.SetTitle('Events')
                yaxis.SetTickLength(0.025)
                yaxis.SetTitleSize(0.08)
                yaxis.SetTitleOffset(0.75)
                yaxis.SetLabelSize(0.06)
                yaxis.SetLabelOffset(0.01)

                if 'yrange' in self.options:
                    stack.SetMinimum(self.options['yrange'][0])
                    stack.SetMaximum(self.options['yrange'][1])
                if 'ndiv' in self.options:
                    yaxis.SetNdivisions(self.options['ndiv'])

                xaxis = stack.GetXaxis()
                xaxis.SetTitleSize(0)
                xaxis.SetLabelSize(0)

                self.main_pad.Update()
                self.main_pad.Modified()
                self.canvas.Update()

                ratio_hist = self.ratio_hists[-1]
                # xaxis
                rxaxis = ratio_hist.GetXaxis()
                if 'xtitle' in self.options:
                    rxaxis.SetTitle(self.options['xtitle'])
                rxaxis.SetTitleSize(0.16)
                rxaxis.SetTitleOffset(0.9)
                rxaxis.SetLabelSize(0.13)
                rxaxis.SetLabelOffset(0.01)
                rxaxis.SetTickLength(0.05)

                # yaxis
                ryaxis = ratio_hist.GetYaxis()
                ryaxis.SetTitle('Ratio')
                ryaxis.SetTitleSize(0.14)
                ryaxis.SetTitleOffset(0.4)
                ryaxis.SetLabelSize(0.12)
                ryaxis.SetLabelOffset(0.01)
                ryaxis.SetTickLength(0.025)
                if 'ratiorange' in self.options:
                    ryaxis.SetRangeUser(self.options['ratiorange'][0], self.options['ratiorange'][1])
                ryaxis.SetNdivisions(503)

            else:
                # not implemented yet
                NotImplementedError("Ratio plots are not implemented for non-ratio mode.")
        
        self.canvas.Modified()
        self.canvas.Update()

        return

    
    def plot_legend(self):
        # Create a legend

        self.legend = ROOT.TLegend(*self.options['legend_pos'])
        self.legend.SetTextSize(0.05)
        self.legend.SetBorderSize(0)
        self.legend.SetFillStyle(0)
        self.legend.SetTextFont(42)

        for i, hist in enumerate(self.stacks):
            stack = self.stacks[hist]['stack']

            hists = stack.GetHists()

            for h in hists:
                if 'legend_opt' in self.options:
                    self.legend.AddEntry(h, h.GetName(), self.options['legend_opt'][i])
                else:
                    self.legend.AddEntry(h, h.GetName())

        self.legend.Draw('same')

    
    def plot_label(self):
        # get position
        pad = self.main_pad if self.nratio else self.canvas.GetPad(0)
        pad_ylow = pad.GetYlowNDC()
        x = pad.GetLeftMargin()
        y = 1 - pad.GetTopMargin()*(1-pad_ylow) + 0.01

        # Draw CMS label
        cmsTex = ROOT.TLatex()
        cmsTex.SetNDC()
        cmsTex.SetTextFont(42)
        cmsTex.SetTextSize(0.05)
        cmsTex.SetTextAlign(11)
        cmsTex.DrawLatex(x, y, '#bf{Private Work}')
        cmsTex.DrawLatex(x+0.25, y, f'#it{{{self.label}}}')

        return


    def plot_textbox(self, textbox):
        self.textbox = ROOT.TLatex()
        self.textbox.SetNDC()
        self.textbox.SetTextFont(42)
        self.textbox.SetTextSize(0.06)
        self.textbox.SetTextAlign(11)
        self.textbox.SetTextColor(ROOT.kBlack)
        self.textbox.SetTextSize(0.06)

        for i, text in enumerate(textbox['text']):
            self.textbox.DrawLatex(textbox['textbox'][0], textbox['textbox'][1]-i*0.07, text)


    def draw_canvas(self, w=800, h=700):
        # Create a canvas
        self.canvas = ROOT.TCanvas("canvas", "canvas", w, h)

        self.setup_pad()
        self.plot_results()

        self.setup_ratio('Data', 'Sim') # TODO: hard coded

        self.canvas.cd()
        self.canvas.Update()

        # Improve visualization
        self.improve_visualization()

        # Plot legend
        if 'legend_pos' in self.options:
            self.plot_legend()

        # Plot label
        if 'label' in self.options:
            self.label = self.options['label']
            self.plot_label()

        # Plot textbox
        if 'textbox' in self.options:
            self.plot_textbox(self.options['textbox'])

        # Update the canvas
        self.canvas.Update()

        return


    def save_canvas(self, savepath, name):
        # Save the canvas
        self.canvas.Modified()
        self.canvas.Update()
        self.canvas.SaveAs(f"{savepath}/{name}.png")
        self.canvas.SaveAs(f"{savepath}/{name}.root")
        self.canvas.SaveAs(f"{savepath}/{name}.pdf")
