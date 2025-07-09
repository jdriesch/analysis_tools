class VariationCollector:
    def __init__(self):
        self.variations = {}

    def add(
            self, name, vtype, processes, 
            val=1.0, tmpl=False, group=False,
            normalize=False
        ):

        if not tmpl:
            tmpl = name

        self.variations[tmpl] = {
            'type': vtype,
            'processes': processes,
            'value': val,
            'group': group,
            'name': name,
            'normalize': normalize
        }

    def provide(self):
        return self.variations


def get_variations(region):
    """
    define variations for the fit
    """

    variations = VariationCollector()

    if region == 'Z':
        all_procs = ['DY', 'EWK', 'TT']
        pdf_procs = ['DY', 'TT']

    else:
        all_procs = ['W', 'EWK', 'TT', 'DY']
        pdf_procs = ['W', 'TT', 'DY']

    # normalization uncertainties
    variations.add('norm_ewk', 'lnN', ['EWK'], val=1.1, group='mc_ewk')
    variations.add('norm_tt', 'lnN', ['TT'], val=1.1, group='mc_tt')

    # uncertainties from Nominal file
    # scale factors
    for sf in ["Trk", "Sta", "ID", "Iso", "Trg", "Prefire"]:
        variations.add('SF'+sf, 'shape', all_procs, tmpl='sf_'+sf.lower(), group='effsys')

    # event weights
    variations.add('puWeight', 'shape', all_procs, tmpl='pog_puweight', group='Pileup', normalize=True)
    variations.add('ptWeight', 'shape', all_procs, tmpl='ptweight', group='pTweight', normalize=True)

    # pdf weights
    for num in range(1, 101):
        name = f'LHEPdfWeight{num}'
        variations.add(name, 'shape', pdf_procs, tmpl=name, group='pdfscale', normalize=True)

    for weight in ['LHEPdfWeightAlphaS', 'LHEScaleWeightMUF', 'LHEScaleWeightMUR', 'LHEScaleWeightMUFMUR', 'PSWeightISR', 'PSWeightFSR']:
        variations.add(weight, 'shape', pdf_procs, tmpl=weight, group='pdfscale', normalize=True)

    # uncertainties from selection variation
    variations.add('LepCorrScale', 'shape', all_procs, tmpl='scale', group='Momentum')
    variations.add('LepCorrResol', 'shape', all_procs, tmpl='resol', group='Momentum')

    if region != 'Z':
        # qcd variations
        for mt in range(1, 21):
            variations.add(f'QCD{region}Bin{mt}', 'shape', [f'QCD{region}'], tmpl=f'bin{mt}', group='QCD')
        variations.add('QCDmcscale', 'shape', [f'QCD{region}'], tmpl='mcscale', group='QCD')

    return variations.provide()


def get_histogram_locations(region):
    """
    locations from output files from histogramming process.
    """

    basepath = f"output/batch_jobs/{region}/"

    locations = [
        basepath+'Nominal/*.root',
        basepath+'scaleup/*.root',
        basepath+'scaledn/*.root',
        basepath+'resolup/*.root',
        basepath+'resoldn/*.root',
    ]

    return locations
