import logging

logger = logging.getLogger(__name__)

class DataCard():
    def __init__(self, save_path, nuisances):
        self.save_path = save_path
        self.nuisances = nuisances
        self.nuisance_groups = {}
        self.processes = {}
        self.regions = {}
        self.all_hists = {}
        self.nprocesses = -1 # starts counting at zero
        self.nsignal = 0
        self.nbackground = 1
        self.nchannels = 0 # starts counting at one


    def add_channel(self):
        self.nchannels += 1

        print("Warning: Currently, this option only increases the channel counter.")

        return
        

    def add_process(self, process, process_type, file, hname):

        if process in self.processes:
            logger.warning(f"Process {process} already present in Datacard. Overwriting...")
        
        if process_type == 'data':
            count = None
            process = 'data_obs'

        elif process_type == 'signal':
            count = self.nsignal
            self.nsignal -= 1
            self.nprocesses += 1

        elif process_type == 'background':
            count = self.nbackground
            self.nbackground += 1
            self.nprocesses += 1

        else:
            raise ValueError(f"Unknown process type '{process_type}' for process '{process}'.")

        self.processes[process] = {
            'file': file,
            'hname': hname,
            'count': count
        }

        return
    

    def construct_nuisance_groups(self):
        """
        construct the nuisance groups
        """

        for nuisance, item in self.nuisances.items():
            group = item['group']
            nuis_name = item['name']

            if group not in self.nuisance_groups:
                self.nuisance_groups[group] = [nuis_name]

            else:
                self.nuisance_groups[group].append(nuis_name)

        return


    def write(self):
        """
        Write the datacard to a text file in CMS Combine format.
        """
        def format_line(label, values, width=25):
            return f"{label:<{width}}" + " ".join(f"{v:<10}" for v in values) + "\n"
        
        def write_line(f):
                f.write("-"*50 + '\n')
                return

        count_sig = 0
        count_bkg = 1
        
        with open(self.save_path, 'w') as f:
            f.write(f"imax {self.nchannels} number of channels\n")
            f.write(f"jmax {self.nprocesses} number of processes\n")
            f.write(f"kmax * number of nuisance parameters (estimated from content)\n")
            write_line(f)

            # shapes line
            for proc, val in self.processes.items():
                nom = val['hname']
                sys = ''
                if proc != 'data_obs':
                    sys = nom+'_$SYSTEMATIC'
                f.write(f"shapes {proc:<10} * {val['file']} {nom} {sys}\n")
            write_line(f)

            # Bin, process, ID, and rate rows
            bin_row    = ["ch1"] * (self.nprocesses + 1)
            proc_names = [p for p in self.processes if p != "data_obs"]
            proc_ids   = [str(self.processes[p]['count']) for p in self.processes if p != "data_obs"]
            rates      = ["1.0"] * (self.nprocesses + 1)

            f.write(format_line("bin", bin_row, 35))
            f.write(format_line("process", proc_names, 35))
            f.write(format_line("process", proc_ids, 35))
            f.write(format_line("rate", rates, 35))
            write_line(f)

            # nuisances
            for nuis, entry in self.nuisances.items():
                nuis_name = entry["name"]
                nuisance_type = entry["type"]
                affected_procs = entry["processes"]
                basevalue = entry["value"]

                values = [basevalue if proc in affected_procs else "-" for proc in proc_names]
                f.write(format_line(nuis_name, [nuisance_type] + values))

            # Nuisance groups
            logger.debug(f"Nuisance groups: {self.nuisance_groups}")
            for group_name, nuis_list in self.nuisance_groups.items():
                f.write(f"{group_name} group = {' '.join(nuis_list)}\n")

        logger.info(f"Datacard written to {self.save_path}")