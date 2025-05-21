This is the pileup correction, aimed at aligning the pileup in the simulation with the pileup in the recorded dataset.
In this code, there are two sets of corrections:

1. the optimal correction set, tailored to the dataset used in this analysis. It is obtained by weighting each simulated event according to the ratio of the measured pileup profile and the true simulated pileup.
The measured pileup profile is obtained from the 'pileupCalc' tool:
https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData#Using_pileupCalc
The true pileup profile can be obtained using the corresponding entries in the simulation (not the reconstructed number of primary vertices, but the true generated!)
2. when considering larger datasets, the centrally provided correctionlib file can be used instead (here denoted with BCD, according to the combination of runs).
