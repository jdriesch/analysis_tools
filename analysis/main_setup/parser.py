from argparse import ArgumentParser, RawTextHelpFormatter


def parse_args():
    parser = ArgumentParser(
        description="Parser for analysis setup",
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        '-H',
        '--histograms',
        action='store_true',
        default=False,
        help="produce histograms from ntuples&friends"
    )
    parser.add_argument(
        '--noIso',
        action='store_true',
        default=False,
        help='skip iso histograms'
    )
    parser.add_argument(
        '--noNom',
        action='store_true',
        default=False,
        help='skip Nominal histogram production'
    )
    parser.add_argument(
        '--noPtVar',
        action='store_true',
        default=False,
        help='skip pt correction histogram production'
    )
    parser.add_argument(
        '--qcd',
        action='store_true',
        default=False,
        help="make qcd extrapolation"
    )
    parser.add_argument(
        '-P',
        '--plot',
        action='store_true',
        default=False,
        help="produce plots from histograms"
    )
    parser.add_argument(
        '--prepare',
        action='store_true',
        default=False,
        help="prepare the fit"
    )
    parser.add_argument(
        '-F',
        '--fit',
        action='store_true',
        default=False,
        help="run the fit"
    )
    parser.add_argument(
        '-A',
        '--analysis',
        action='store_true',
        default=False,
        help="run the analysis"
    )
    parser.add_argument(
        '--local',
        action='store_true',
        default=False,
        help="run locally"
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help="run in debug mode"
    )
    

    args = parser.parse_args()
    return args