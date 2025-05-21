sample_tmpl = '{}_TuneCP5_13p6TeV_{}-pythia8_Run3Summer22NanoAODv12-130X'

samples = {
    "DY": [
        sample_tmpl.format("DYto2L-2Jets_MLL-10to50", "amcatnloFXFX"),
        sample_tmpl.format("DYto2L-2Jets_MLL-50", "amcatnloFXFX"),
    ],
    "W": [
        sample_tmpl.format("WtoLNu-2Jets", "amcatnloFXFX"),
    ],
    "TT": [
        sample_tmpl.format("TT", "powheg"),
    ],
    "ST": [
        sample_tmpl.format("TbarBQ_t-channel_4FS", "powheg-madspin"),
        sample_tmpl.format("TbarWplus_DR_AtLeastOneLepton", "powheg"),
        sample_tmpl.format("TBbarQ_t-channel_4FS", "powheg-madspin"),
        sample_tmpl.format("TWminus_DR_AtLeastOneLepton", "powheg"),
    ],
    "VV": [
        sample_tmpl.format("WWto2L2Nu", "powheg"),
        sample_tmpl.format("WWtoLNu2Q", "powheg"),
        sample_tmpl.format("WZto2L2Q", "powheg"),
        sample_tmpl.format("WZto3LNu", "powheg"),
        sample_tmpl.format("WZtoLNu2Q", "powheg"),
        sample_tmpl.format("ZZto2L2Nu", "powheg"),
        sample_tmpl.format("ZZto2L2Q", "powheg"),
        sample_tmpl.format("ZZto2Nu2Q", "powheg"),
        sample_tmpl.format("ZZto4L", "powheg"),
    ],
    "VBF": [
        sample_tmpl.format("VBFto2L_MLL-50", "madgraph"),
        sample_tmpl.format("VBFtoLNu", "madgraph"),
    ],
    "DYtau": [
        sample_tmpl.format("DYto2L-2Jets_MLL-10to50", "amcatnloFXFX"),
        sample_tmpl.format("DYto2L-2Jets_MLL-50", "amcatnloFXFX"),
    ],
    "Wtau": [
        sample_tmpl.format("WtoLNu-2Jets", "amcatnloFXFX"),
    ],
    "Wnonfid": [
        sample_tmpl.format("WtoLNu-2Jets", "amcatnloFXFX"),
    ],
    "DYnonfid": [
        sample_tmpl.format("DYto2L-2Jets_MLL-10to50", "amcatnloFXFX"),
        sample_tmpl.format("DYto2L-2Jets_MLL-50", "amcatnloFXFX"),
    ],
    "Data": [
        "SingleMuon_Run2022C-22Sep2023-v1",
        "Muon_Run2022C-22Sep2023-v1",
    ]
}