def create_job_script(job_script, input_file, job_dir):
    with open(job_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("echo 'Starting batch job'\n")
        f.write(
            "source /cvmfs/sft.cern.ch/lcg/views/"\
            "LCG_105/x86_64-el9-gcc11-opt/setup.sh\n"
        )
        f.write(f'cd {job_dir}\n')
        f.write(f"python hist_process.py {input_file} $1")


def create_submit_script(submit_script, job_script, n_processes):
    import os

    log_dir = os.path.dirname(submit_script)+ '/logs'
    os.makedirs(log_dir, exist_ok=True)

    with open(submit_script, 'w') as f:
        f.write(f'executable = {job_script}\n')
        f.write('arguments = $(Process)\n')
        f.write('\n')
        f.write('# Output/Error/Log files\n')
        f.write(f'Output = {log_dir}/job_$(Cluster)_$(Process).out\n')
        f.write(f'Error  = {log_dir}/job_$(Cluster)_$(Process).err\n')
        f.write(f'Log    = {log_dir}/job_$(Cluster)_$(Process).log\n')
        f.write('\n')
        f.write('# job requirements\n')
        f.write('+RequestWalltime = 3600*2\n')
        f.write('RequestCPUs = 1\n')
        f.write('RequestMemory = 2000\n')
        f.write('request_disk = 5000000\n')
        f.write('Requirements = TARGET.ProvidesEKPResources =?= True\n')
        f.write('accounting_group = cms.higgs\n')
        f.write('Universe = docker\n')
        f.write('docker_image = cverstege/alma9-gridjob\n')
        f.write('getenv = True\n')

        f.write(f'queue {n_processes}\n')
