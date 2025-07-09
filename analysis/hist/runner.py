import logging

import config as cfg

from .hist_manager import ProcessManager
from .qcd import extrapolate_all

logger = logging.getLogger(__name__)


def run_production(args):
    logger.info("Running the histogram production mode.")

    region_selections = cfg.selections.get_region_selections(args)

    for region in region_selections:
        logger.info(f"Processing region {region}...")
        logger.debug(f"Options are: {region_selections[region]}")

        samples = cfg.samples.get_samples(region)
        process_selections = cfg.selections.get_process_selection(region)

        for variation in region_selections[region]:

            histograms = cfg.binnings.get_histograms(region, variation)
            definitions = cfg.definitions.get_definitions(variation)

            process_manager = ProcessManager(
                region=region,
                files=samples,
                filters={
                    "region": region_selections,
                    "process": process_selections,
                },
                definitions=definitions,
                selection=variation,
                binnings=histograms,
                friends=['sf', 'xy', 'pu', 'ptweight', 'xsec', 'xy', 'lepton', 'met_punom'],
                nthreads=1
            )

            if args.local:
                process_manager.run_local()
            else:
                process_manager.run_batch(args.version, args.log)

# TODO: remove dependencies (friends, paths,...)


def run_qcd(version):

    for region in ['Wp', 'Wm']:
        save_option = 'recreate'

        for mcscale in [0.9, 1, 1.1]:
            save_dir = f'output/{version}/batch_jobs/{region}/Nominal/QCD{region}_QCD{region}.root'
            extrapolate_all(region, mcscale, save_dir, save_option)
            save_option = 'update'