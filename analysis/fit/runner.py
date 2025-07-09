from glob import glob
import logging
import os

import ROOT

import config as cfg
from .datacards import DataCard
from .prepare import PrepareFit

logger = logging.getLogger(__name__)

def collect_histograms():
    """
    Collect all relevant histograms and save them to common file.
    """

    path_tosave = 'output/root/'
    
    for region in ['Wp', 'Wm', 'Z']:
        all_hists = {}
        
        # load config parameters
        hist_locations = cfg.variations.get_histogram_locations(region)
        nuisances = cfg.variations.get_variations(region)
        variables = cfg.binnings.get_histograms(region)

        # extract varname
        varname = list(variables.keys())[0]

        # get list of all relevant files with histograms
        all_files = []
        for loc in hist_locations:
            all_files += glob(loc)

        # save histograms with new names
        save_path = path_tosave+region+'.root'

        # go through various preparation steps
        prepare_fit = PrepareFit(varname, nuisances, region)
        prepare_fit.register_histograms(all_files)
        prepare_fit.normalize_histograms()
        prepare_fit.save_histograms(save_path)

    return

    # TODO: add histograms from MET variation.


def make_datacard():

    for region in ['Wp', 'Wm', 'Z']:
        variations = cfg.variations.get_variations(region)
        fit_variable = list(cfg.binnings.get_histograms(region, 'Nominal').keys())[0]

        card_path = f'output/cards/{region}.txt'
        os.makedirs('output/cards/', exist_ok=True)

        base_path = '/work/jdriesch/earlyrun3/analysis/analysis_tools/analysis/output/'
    
        hist_path = base_path + f'root/{region}.root'

        datacard = DataCard(card_path, variations)

        # add all channels
        datacard.add_channel()

        # add all processes
        processes = cfg.selections.get_region_categories(region)

        for proc_type in processes:
            for proc in processes[proc_type]:
                hname = f'{proc}_{fit_variable}'
                datacard.add_process(proc, proc_type, hist_path, hname)

        datacard.construct_nuisance_groups()

        datacard.write()

    return
        