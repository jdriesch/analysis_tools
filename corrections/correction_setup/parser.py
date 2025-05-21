import argparse

def setup():
    parser = argparse.ArgumentParser(
        description="""This is the correction handler. The general idea is \
            to derive the different corrections to objects in data/sim \
            step by step on top of each other.
            """)
    
    parser.add_argument(
        "--pileup",
        action="store_true",
        help="Apply pileup correction"
    )
    parser.add_argument(
        "--bosonpt",
        action="store_true",
        help="Apply boson pT correction"
    )
    parser.add_argument(
        "--sf",
        action="store_true",
        help="Apply scale factor correction"
    )
    parser.add_argument(
        "--xy",
        action="store_true",
        help="Apply MET xy correction"
    )
    parser.add_argument(
        "--scare",
        action="store_true",
        help="Apply muon scale and resolution correction"
    )
    parser.add_argument(
        "--recoil",
        action="store_true",
        help="Apply recoil correction"
    )
    parser.add_argument(
        "--qcd",
        action="store_true",
        help="Apply QCD estimation"
    )

    # additional options
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        '-j',
        '--jobs',
        type=int,
        default=1,
        help="Number of jobs to run in parallel"
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help="Overwrite existing files"
    )

    args = parser.parse_args()
    return args