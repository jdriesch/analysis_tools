import logging


main_logger = logging.getLogger(__name__)


def run_pipeline(args):

    if args.histograms:
        from hist import run_production
        run_production(args)

    if args.qcd:
        from hist import run_qcd
        run_qcd(args.version)

    if args.prepare:
        from fit import collect_histograms, make_datacard
        collect_histograms(args.version)
        make_datacard()
    