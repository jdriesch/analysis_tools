def get_base_selection(channel, corr=""):

    if channel=='mm':
        acceptance = (
            f"( pt_1{corr}>25. && pt_2{corr}>25. && "
            "abs(eta_1) < 2.4 && abs(eta_2) < 2.4)"
        )
        id = "(tightId_1 && tightId_2)"
        iso = "(iso_1 < 0.15 && iso_2 < 0.15)"
        trg = "(trg_single_mu24_1 || trg_single_mu24_2)"
        add = (
            f"(q_1*q_2 < 0)"
            f"(m_vis{corr} > 60. && m_vis{corr} < 120.)"
            "(pog_puweight < 100)"
        )

    elif channel=='mmet':
        acceptance = f"(pt_1{corr}>25. && abs(eta_1) < 2.4)"
        id = "(tightId_1)"
        iso = "(iso_1 < 0.15)"
        trg = "(trg_single_mu24_1)"
        add = "(extramuon_veto == 1)"

    else:
        raise ValueError(
            f"Unknown channel: {channel}. "\
            "Supported channels are 'mm' and 'mmet'."
        )
    
    base_selection = {
        'acceptance': acceptance,
        'id': id,
        'iso': iso,
        'trg': trg,
        'add': add
    }

    return base_selection


def update_selection(base_selection, isos=False, zpt=False):
    """
    Cover special cases, where the base selections are not
    fully applied.
    """
    new_selection = {}

    if isos:
        # non isoated W region
        base_selection["iso"] = ""
        for n in range(len(isos)-1):
            new_selection[f'Iso{n}'] = f'(iso_1 > {isos[n]} && iso_1 < {isos[n+1]})'

    elif zpt:
        # zpt binning
        # TODO: update this section
        new_selection = {}

    return base_selection, new_selection


def get_process_selection(channel):
    """
    Get the process selection for the analysis.
    """
    if channel == 'mm':
        dy = [
            'is_dy_tt != 1',
            'genmatch_pt_1 > 25 && genmatch_pt_2 > 25',
            'abs(genmatch_eta_1) < 2.4 && abs(genmatch_eta_2) < 2.4',
            'gen_m_vis > 60 && gen_m_vis < 120'
        ]
        dytau = ['is_dy_tt == 1']
        dynonfid = [
            'is_dy_tt != 1',
            '((genmatch_pt_1 <= 25 || genmatch_pt_2 <= 25) ||'\
            '(abs(genmatch_eta_1) >= 2.4 || abs(genmatch_eta_2) >= 2.4) ||'\
            '(gen_m_vis <= 60 || gen_m_vis >= 120))'
        ]

        # define all processes in this signal region    
        process_selection = {
            "DY": {"DY": dy},
            "EWK": {
                "VV": [],
                "ST": [],
                "VBF": [],
                "DYtau": dytau,
                "DYnonfid": dynonfid,
            },
            "TT": {"TT": []},
            "Data": {"Data": []}
        }
        
    elif channel == 'mmet':
        dy = [
            'is_dy_tt != 1',
            'genmatch_pt_1 > 25',
            'abs(genmatch_eta_1) < 2.4'
        ]
        w = [
            'gen_match_1 != 15',
            'genmatch_pt_1 > 25',
            'abs(genmatch_eta_1) < 2.4'
        ]
        dytau = ['is_dy_tt == 1']
        wtau = ['gen_match_1 == 15']
        wnonfid = [
            'gen_match_1 != 15',
            '((genmatch_pt_1 <= 25) || (abs(genmatch_eta_1) >= 2.4))'
        ]
        dynonfid = [
            'is_dy_tt != 1',
            '((genmatch_pt_1 <= 25) || (abs(genmatch_eta_1) >= 2.4))'
        ]

        # define all processes in this signal region    
        process_selection = {
            "W": {"W": w},
            "DY": {"DY": dy},
            "EWK": {
                "VV": [],
                "ST": [],
                "VBF": [],
                "Wtau": wtau,
                "DYtau": dytau,
                "Wnonfid": wnonfid,
                "DYnonfid": dynonfid,
            },
            "TT": {"TT": []},
            "Data": {"Data": []}
        }

    else:
        raise ValueError(
            f"Unknown channel: {channel}. "\
            "Supported channels are 'mm' and 'mmet'."
        )

    return process_selection