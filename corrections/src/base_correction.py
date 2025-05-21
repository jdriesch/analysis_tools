import ROOT
import os
import logging
import glob

class BaseCorrection:
    def __init__(self, inpath, correction, args):
        self.infiles = glob.glob(inpath)
        self.correction = correction
        self.overwrite = args.overwrite
        self.logger = logging.getLogger(__name__)
        self.nthreads = args.jobs


    def execute(self):
        pass


    def check_zombie(self, f):
        """
        Check if the file is a zombie file.
        If it is, remove it and return 0. If it is not, return 1.
        """
        if not os.path.isfile(f):
            return False
        f_tmp = None
        try:
            f_tmp = ROOT.TFile(f)
            if f_tmp and not f_tmp.IsZombie():
                return True
        except OSError:
            self.logger.warning(
                f"OSError encountered while opening file '{f}'. Removing it."
            )
            os.remove(f)
        finally:
            if f_tmp:
                f_tmp.Close()

        if os.path.isfile(f):
            self.logger.warning(
                f"File '{f}' is a zombie file. Removing it."
            )
            os.remove(f)
        return False
    

    def check_file(self, f):
        f_out = f.replace("ntuples", f"friends/{self.correction}")

        # check if output file already exists and is correct
        if self.check_zombie(f_out) and not self.overwrite:
            self.logger.info(f"File {f_out} already exists. Skipping.")
            return False
        # check if output directory exists
        outpath = f_out.replace(f_out.split('/')[-1], '')
        os.makedirs(outpath, exist_ok=True)

        return f_out


    def job_wrapper(self, args):
        return self.execute(*args)


    def run_multicore(self, arguments, nthreads):
        from multiprocessing import Pool, RLock
        from tqdm import tqdm

        pool = Pool(nthreads, initargs=(RLock(),), initializer=tqdm.set_lock)
        for _ in tqdm(
            pool.imap_unordered(self.job_wrapper, arguments),
            total=len(arguments),
            desc="Total progess",
            dynamic_ncols=True,
            leave=True,
            ):
            pass


    def load_chains(self, f_in, friends):
        """
        Load the ROOT dataframe from the input file.
        """

        chain = ROOT.TChain('ntuple')
        chain.Add(f_in)

        friend_chains = {}
        for friend in friends:
            f_friend = f_in.replace("ntuples", f"friends/{friend}")
            # print(f_friend)
            chain_friend = ROOT.TChain('ntuple')
            chain_friend.Add(f_friend)
            chain.AddFriend(chain_friend)

        return chain


    def run_batch(self):
        pass



# make correction histograms

# calculate quantities from the calculated histograms

# apply corrections to the data / sim

# check the results