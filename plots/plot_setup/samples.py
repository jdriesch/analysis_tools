def get_samples(channel):

    basepath = '/ceph/jdriesch/CROWN_samples/test/ntuples/2022/'

    sample_tmpl = '{}_TuneCP5_13p6TeV_{}-pythia8_Run3Summer22NanoAODv12-130X'

    tmpl = basepath + sample_tmpl + '/' + channel + '/*.root'
    print(tmpl)

    samples = {
        "DY": [
            tmpl.format("DYto2L-2Jets_MLL-10to50", "amcatnloFXFX"),
            tmpl.format("DYto2L-2Jets_MLL-50", "amcatnloFXFX"),
        ],
        "W": [
            tmpl.format("WtoLNu-2Jets", "amcatnloFXFX"),
        ],
        "TT": [
            tmpl.format("TT", "powheg"),
        ],
        "ST": [
            tmpl.format("TbarBQ_t-channel_4FS", "powheg-madspin"),
            tmpl.format("TbarWplus_DR_AtLeastOneLepton", "powheg"),
            tmpl.format("TBbarQ_t-channel_4FS", "powheg-madspin"),
            tmpl.format("TWminus_DR_AtLeastOneLepton", "powheg"),
        ],
        "VV": [
            tmpl.format("WWto2L2Nu", "powheg"),
            tmpl.format("WWtoLNu2Q", "powheg"),
            tmpl.format("WZto2L2Q", "powheg"),
            tmpl.format("WZto3LNu", "powheg"),
            tmpl.format("WZtoLNu2Q", "powheg"),
            tmpl.format("ZZto2L2Nu", "powheg"),
            tmpl.format("ZZto2L2Q", "powheg"),
            tmpl.format("ZZto2Nu2Q", "powheg"),
            tmpl.format("ZZto4L", "powheg"),
        ],
        "VBF": [
            tmpl.format("VBFto2L_MLL-50", "madgraph"),
            tmpl.format("VBFtoLNu", "madgraph"),
        ],
        "DYtau": [
            tmpl.format("DYto2L-2Jets_MLL-10to50", "amcatnloFXFX"),
            tmpl.format("DYto2L-2Jets_MLL-50", "amcatnloFXFX"),
        ],
        "Wtau": [
            tmpl.format("WtoLNu-2Jets", "amcatnloFXFX"),
        ],
        "Wnonfid": [
            tmpl.format("WtoLNu-2Jets", "amcatnloFXFX"),
        ],
        "DYnonfid": [
            tmpl.format("DYto2L-2Jets_MLL-10to50", "amcatnloFXFX"),
            tmpl.format("DYto2L-2Jets_MLL-50", "amcatnloFXFX"),
        ],
        "Data": [
            basepath+"SingleMuon_Run2022C-22Sep2023-v1/"+channel+'/*.root',
            basepath+"Muon_Run2022C-22Sep2023-v1/"+channel+'/*.root',
        ]
    }

    return samples