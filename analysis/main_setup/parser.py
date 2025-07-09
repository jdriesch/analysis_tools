from argparse import ArgumentParser, RawTextHelpFormatter
import os
import subprocess


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
    parser.add_argument(
        '--log',
        action='store_true',
        default=False,
        help='enable logging to file.'
    )
    parser.add_argument(
        '-V',
        '--version',
        type=str,
        default='v1',
        help="version number of output files."
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        default=False,
        help="overwrite existing output directory"
    )
    

    args = parser.parse_args()

    args = check_arguments(args)

    return args


def check_arguments(args):

    # version
    if os.path.exists(f'output/{args.version}/') and not args.overwrite:
        overwrite = input(
            f"Output directory {args.version} already exists. "
            "Potentially overwrite? (y/n): "
        ).strip().lower()

        if overwrite != 'y':
            raise ValueError(
                f"Output directory {args.version} already exists. Please "
                "choose a different version or remove the existing directory."
            )
        else:
            print(f"Potentially overwriting output directory {args.version}.")

    # check for uncommitted changes
    status = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True, text=True, check=True
    )

    if status.stdout.strip():
        proceed = input(
            "There are uncommitted changes in the repository. "
            "Proceed? (y/n): "
        ).strip().lower()

        if proceed != 'y':
            raise ValueError(
                "Uncommitted changes found. Please commit or stash your changes "
                "before proceeding."
            )

        else:
            print("Proceeding with uncommitted changes. Adding 'test' to version.")
            args.version += '_test'

    # add information text file with current commit
    commit = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        capture_output=True, text=True, check=True
    )
    commit_hash = commit.stdout.strip()
    with open(f'output/{args.version}/info.txt', 'w') as f:
        f.write(f"Commit hash: {commit_hash}\n")
        f.write(f"Version: {args.version}\n")
        f.write("This file contains the commit hash and version used for this analysis.\n")

    return args