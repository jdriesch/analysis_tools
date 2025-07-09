import ROOT
from glob import glob
import os
import json

from .hist_process import HistMaker
from main_setup.batch import create_job_script, create_submit_script
from config.weights import get_weights

import logging

# make all plots of different variations
# type 1: update the weight
# type 2: update the observable

logger = logging.getLogger(__name__)


class ProcessManager:
    """
    Class to manage different process classes.
    I.e., steer the class
    """

    def __init__(
        self, 
        region,
        files, friends = [], 
        definitions={}, filters={},
        binnings={}, save_path='',
        selection='Nominal',
        nthreads=1
    ):
        """
        Initialize the histogram class.
        """
        self.region = region
        self.files = files
        self.friends = friends
        self.definitions = definitions
        self.region_selection = filters['region']
        self.process_selection = filters['process']
        self.hists = binnings
        self.selection = selection
        self.histograms = []

        self.nthreads = nthreads

        for proc in self.files:
            if isinstance(proc, str):
                self.samples = glob(proc)
            else:
                self.files = proc

        return
    

    def run_local(self):
        """
        Collect all histograms and then save them to commong file.
        """

        raise NotImplementedError("This function is not yet implemented.")


    def run_batch(self, version, dolog):
        """
        Create the histograms in batch mode.
        For this: make one file containing all options
        """

        batch_dir = f'output/{version}/batch_jobs/{self.region}/{self.selection}'
        os.makedirs(batch_dir, exist_ok=True)
        batch_dir_abs = os.path.abspath(batch_dir)
        logger.info(f"Batch directory: {batch_dir_abs}")
        logger.info("Preparing batch jobs...")

        option_dicts = []

        for i, cat in enumerate(self.process_selection):
            for proc in self.process_selection[cat]:
                option_dicts.append(
                    {
                        'files': self.files[proc],
                        'cat': cat,
                        'proc': proc,
                        'friends': self.friends,
                        'definitions': self.definitions,
                        'region_selection': self.region_selection[self.region][self.selection],
                        'process_selection': self.process_selection[cat][proc],
                        'weights': get_weights(proc, self.selection),
                        'nthreads': self.nthreads,
                        'hists': self.hists,
                        'save_path': batch_dir_abs+ f'/{proc}_{cat}.root'
                    }
                )
                logger.info(f"Preparing batch job for {proc} in category {cat}")

        # save options to a json file
        options_file = os.path.join(batch_dir, 'options.json')
        with open(options_file, 'w') as f:
            json.dump(option_dicts, f, indent=4)
        logger.info(f"Saved options to {options_file}")

        # create the job script
        n_processes = len(option_dicts)

        job_script = os.path.join(batch_dir, f"job.sh")
        submit_script = os.path.join(batch_dir, f"submit.sub")
        job_dir = os.path.abspath(__file__).replace('hist_manager.py', '')

        options_file_abs = os.path.abspath(options_file)
        job_script_abs = os.path.abspath(job_script)

        create_job_script(job_script, options_file_abs, job_dir)
        create_submit_script(dolog, submit_script, job_script_abs, n_processes)

        # make sure the scripts are executable
        os.chmod(job_script, 0o755)
        os.chmod(submit_script, 0o644)

        logger.info(f"Created job script {job_script} and submit script {submit_script}")

        # submit the job
        os.system(f"condor_submit {submit_script}")
        logger.info(f"Submitted job with {n_processes} processes.")
        return


    def run(self, local=True):
        """
        Run the histogram creation process.
        """
        if local:
            self.run_local()
        else:
            self.run_batch()


# TODO: add method to run the histograms such that a max number of events is processed in one job