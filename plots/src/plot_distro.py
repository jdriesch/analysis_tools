import ROOT

ROOT.gROOT.SetBatch(True)

class PlotDistro:
    def __init__(self, loadpath, savepath, options):
        self.loadpath = loadpath
        self.savepath = savepath
        self.options = options
        self.hists = []
        self.ratio_hists = []
        self.drawn_objects = []

        self.nratio = True # hard-coded for now

        self.load_hists()


    def get_process(self, proc):
        """
        Add subprocesses, e.g. 'EWK' consisting of ST, VV,...
        """
        # Load subprocesses from the options
        subprocesses = proc['subprocesses']
        name = proc['process']
        options = proc['options']

        for i, subprocess in enumerate(subprocesses):
            if i==0:
                hist = self.tf.Get(subprocess + self.options['name']).Clone(name)
                hist.SetDirectory(0)
            else:
                hist_toadd = self.tf.Get(subprocess + self.options['name']).Clone(name)
                hist_toadd.SetDirectory(0)
                hist.Add(hist_toadd)

        # Set histogram properties
        hist = self.set_properties(hist, options)

        return hist


    def construct_group(self, group):
        """
        Construct the groups of processes, e.g. 'Data', 'Sim'
        """
        stack = ROOT.THStack(group, '')

        for proc in self.options['process_groups'][group]['categories']:
            hist = self.get_process(proc)
            # print(hist.GetName(), hist.GetEntries(), hist.GetFillColor())

            self.hists.append(hist)
            stack.Add(hist)

        return stack
    

    def load_hists(self):
        # Load the ROOT file
        self.tf = ROOT.TFile(self.loadpath, 'read')

        self.stacks = {}

        for group in self.options['process_groups']:
            # Construct the group of processes
            self.stacks[group] = {
                'stack': self.construct_group(group),
                'draw_opt': self.options['process_groups'][group]['draw_opt'],
            }

        self.tf.Close()


    def set_properties(self, hist, options):
        # Set the histogram properties

        if 'linecolor' in options:
            hist.SetLineColor(options['linecolor'])

        if 'linestyle' in options:
            hist.SetLineStyle(options['linestyle'])

        if 'fillcolor' in options:
            hist.SetFillColor(options['fillcolor'])

        if 'fillstyle' in options:
            hist.SetFillStyle(options['fillstyle'])

        if 'markerstyle' in options:
            hist.SetMarkerStyle(options['markerstyle'])

        if 'markersize' in options:
            hist.SetMarkerSize(options['markersize'])

        if 'linewidths' in options:
            hist.SetLineWidth(options['linewidths'])

        if 'xtitle' in options:
            hist.GetXaxis().SetTitle(options['xtitle'])

        if 'ytitle' in options:
            hist.GetYaxis().SetTitle(options['ytitle'])
 
        hist.SetTitle('')

        # axes
        xaxis = hist.GetXaxis()
        xaxis.SetTickLength(0.03)

        if 'xrange' in options:
            xaxis.SetRangeUser(options['xrange'][0], options['xrange'][1])

        return hist


    def setup_ratio(self, num, den):
        hist_num = self.stacks[num]['stack'].GetStack().Last().Clone(num + "_ratio")
        hist_den = self.stacks[den]['stack'].GetStack().Last().Clone(den + "_ratio")

        hist_num.Divide(hist_den)

        hist_num.Draw(self.stacks[num]['draw_opt'])

        self.ratio_hists.append(hist_num)


    def setup_pad(self):
        # Create a main pad and a ratio pad
        if self.nratio:
            self.main_pad = ROOT.TPad("main_pad", "main_pad", 0, 0.35, 1, 1)
            self.main_pad.Draw()
            self.main_pad.SetBottomMargin(0.025)
            self.main_pad.SetRightMargin(0.03)
            self.main_pad.SetLeftMargin(0.12)

            # ratio pad
            self.ratio_pad = ROOT.TPad("ratio_pad", "ratio_pad", 0, 0, 1, 0.35)
            self.ratio_pad.Draw()
            self.ratio_pad.SetTopMargin(0.05)
            self.ratio_pad.SetBottomMargin(0.35)
            self.ratio_pad.SetRightMargin(0.03)
            self.ratio_pad.SetLeftMargin(0.12)

            self.main_pad.cd()

        else:
            # self.main_pad = ROOT.TPad("main_pad", "main_pad", 0, 0, 1, 1)
            # self.main_pad.cd()
            self.canvas.cd()


    def improve_visualization(self):
        # get the histogram responsible for the axes
        # hist = self.stacks[-1]
        for group in self.stacks:
            stack = self.stacks[group]['stack']
            print(self.stacks)
            if self.nratio:
                yaxis = stack.GetYaxis()
                yaxis.SetTickLength(0.025)
                yaxis.SetTitleSize(0.08)
                yaxis.SetTitleOffset(0.75)
                yaxis.SetLabelSize(0.06)
                yaxis.SetLabelOffset(0.01)

                if 'yrange' in self.options:
                    yaxis.SetRangeUser(self.options['yrange'][0], self.options['yrange'][1])
                if 'ndiv' in self.options:
                    yaxis.SetNdivisions(self.options['ndiv'])

                stack.GetXaxis().SetTitleSize(0)
                stack.GetXaxis().SetLabelSize(0)

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
                # xaxis
                xaxis = stack.GetXaxis()
                xaxis.SetTitle(self.options['xtitle'])
                xaxis.SetTitleSize(0.06)
                xaxis.SetTitleOffset(0.9)
                xaxis.SetLabelSize(0.06)
                xaxis.SetLabelOffset(0.01)
                xaxis.SetTickLength(0.03)

                # yaxis
                yaxis = stack.GetYaxis()
                yaxis.SetTitle(self.options['ytitle'])
                yaxis.SetTitleSize(0.06)
                yaxis.SetTitleOffset(0.75)
                yaxis.SetLabelSize(0.06)
                yaxis.SetLabelOffset(0.01)
                yaxis.SetTickLength(0.03)
                yaxis.SetRangeUser(self.options['yrange'][0], self.options['yrange'][1])

        
        self.canvas.Modified()
        self.canvas.Update()

    
    def plot_label(self):
        # get position
        pad = self.main_pad if self.nratio else self.canvas.GetPad(0)
        x = pad.GetLeftMargin()
        y = pad.GetTopMargin()

        cmsTex = ROOT.TLatex()
        cmsTex.SetNDC()
        cmsTex.SetTextFont(42)
        cmsTex.SetTextSize(0.07)
        cmsTex.SetTextAlign(11)
        cmsTex.DrawLatex(x, 1-y + 0.015, '#bf{Private Work}')
        cmsTex.DrawLatex(x+0.23, 1-y + 0.015, '#it{'+self.label+'}')


    def plot_results(self):
        if 'draw_order' in self.options:
            # Draw the stacks in the order specified in the options
            for group in self.options['draw_order']:
                if group in self.stacks:
                    stack = self.stacks[group]['stack']
                    stack.Draw(self.stacks[group]['draw_opt'])

                    self.drawn_objects.append(stack)
                else:
                    print(f"Warning: Group '{group}' not found in stacks.")

        else:
            for group in self.stacks:
                # Draw the histograms in the main pad
                self.stacks[group]['stack'].Draw(self.stacks[group]['draw_opt'])
                # print(self.stacks[group]['stack'].GetMaximum())


        self.canvas.Modified()
        # self.canvas.Update()


    def plot_ratio(self):
        # Create a ratio histogram
        self.ratio_pad.cd()

        draw_options = []

        for i, hist in enumerate(self.stacks[:self.nratio]):
            ratio_hist = hist.Clone(hist.GetName() + "_ratio")
            ratio_hist.Divide(self.stacks[1])
            
            for n in range(1, ratio_hist.GetNbinsX() + 1):
                if self.stacks[1].GetBinContent(n) == 0:
                    if hist.GetBinContent(n) == 0:
                        ratio_hist.SetBinContent(n, 1)
                    else:
                        ratio_hist.SetBinContent(n, 100)

            self.ratio_hists.append(ratio_hist)
            draw_options.append(self.options['draw_opt'][i])


        # Draw the ratio histogram
        for i, draw_option in reversed(list(enumerate(draw_options))):
            self.ratio_hists[i].Draw(draw_option)

        self.canvas.Modified()
        self.canvas.Update()
        # self.ratio_pad.Update()
        self.main_pad.cd()

    
    def plot_legend(self):
        # Create a legend

        self.legend = ROOT.TLegend(*self.options['legend_pos'])
        self.legend.SetTextSize(0.07)
        self.legend.SetBorderSize(0)
        self.legend.SetFillStyle(0)
        self.legend.SetTextFont(42)

        for i, hist in enumerate(self.stacks):
            if self.options['legend_opt'][i]:
                self.legend.AddEntry(hist, self.options['legend'][i], self.options['legend_opt'][i])
            else:
                self.legend.AddEntry(hist, self.options['legend'][i])

        self.legend.Draw('same')

    
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


    def draw_canvas(self):
        # Create a canvas
        self.canvas = ROOT.TCanvas("canvas", "canvas", 800, 800)
        self.canvas.SetTopMargin(0.05)
        self.canvas.SetBottomMargin(0.15)
        self.canvas.SetRightMargin(0.03)
        self.canvas.SetLeftMargin(0.12)

        self.setup_pad()

        self.plot_results()

        self.ratio_pad.cd()
        self.setup_ratio('Data', 'Sim') # TODO: hard coded

        # Improve visualization
        self.improve_visualization()

        # Plot legend
        if 'legend' in self.options:
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


    def save_canvas(self, savepath, name):
        # Save the canvas
        self.canvas.SaveAs(f"{savepath}/{name}.pdf")
        self.canvas.SaveAs(f"{savepath}/{name}.png")
        self.canvas.SaveAs(f"{savepath}/{name}.root")



if __name__ == "__main__":
    # Example usage
    loadpath = "test.root"
    savepath = "test"

    options = {
        'process_groups': {
            'Data': {
                'categories': [
                    {'process': 'Data', 'subprocesses': ['Data'], 'options': {'markerstyle': 20}}
                ],
                'draw_opt': 'e1p x0 same'
            },
            'Sim': {
                'categories': [
                    {'process': 'EWK', 'subprocesses': ['ST', 'VV', 'DYnonfid', 'DYtau', 'VBF'], 'options': {'fillcolor': ROOT.kGreen-8}},
                    {'process': 'TT', 'subprocesses': ['TT'], 'options': {'fillcolor': ROOT.kMagenta+3}},
                    {'process': 'DY', 'subprocesses': ['DY'], 'options': {'fillcolor': ROOT.kAzure+1}},
                ],
                'draw_opt': 'hist'
            }
        },  
        'name': 'm_visNominal',
        'xtitle': 'm_{vis} (GeV)',
        'ratiorange': [0.9, 1.1],
        'draw_order': ['Sim', 'Data']
    }

    plotter = PlotDistro(loadpath, savepath, options)
    plotter.draw_canvas()
    plotter.save_canvas(savepath, "plot_distro")