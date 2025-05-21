def get_base_selection(channel, corr_postfix=""):

    if channel=='mm':
        base_selection = {
            "acceptance": f"(pt_1{corr_postfix}>25. && pt_2{corr_postfix}>25. && abs(eta_1) < 2.4 && abs(eta_2) < 2.4)",
            "tight_id": "(tightId_1 && tightId_2)",
            "opposite_charge": "(q_1*q_2 < 0)",
            "lepton_iso": "(iso_1 < 0.15 && iso_2 < 0.15)",
            "Z_mass_window": f"(m_vis{corr_postfix} > 60. && m_vis{corr_postfix} < 120.)",
            "pu_truncation": "(pog_puweight < 100)",
            "trg_matching": "(trg_single_mu24_1 || trg_single_mu24_2)",
        }
    elif channel=='mmet':
        base_selection = {
            "acceptance": f"(pt_1{corr_postfix}>25. && abs(eta_1) < 2.4)",
            "tight_id": "(tightId_1)",
            "lepton_iso": "(iso_1 < 0.15)",
            "extramuon_veto": "(extramuon_veto == 1)",
            "trg_matching": "(trg_single_mu24_1)",
        }
    else:
        raise ValueError(f"Unknown channel: {channel}. Supported channels are 'mm' and 'mmet'.")
    
    return base_selection


def get_process_selection(channel):
    """
    Get the process selection for the analysis.
    """
    if channel == 'mm':
        process_selection = {
            "DY": [
                'is_dy_tt != 1',
                'genmatch_pt_1 > 25 && genmatch_pt_2 > 25',
                'abs(genmatch_eta_1) < 2.4 && abs(genmatch_eta_2) < 2.4',
                'gen_m_vis > 60 && gen_m_vis < 120'
            ],
            "TT": [],
            "VV": [],
            "ST": [],
            "VBF": [],
            "DYtau": [
                'is_dy_tt == 1'
            ],
            "DYnonfid": [
                'is_dy_tt != 1',
                '((genmatch_pt_1 <= 25 || genmatch_pt_2 <= 25) ||'\
                ' (abs(genmatch_eta_1) >= 2.4 || abs(genmatch_eta_2) >= 2.4) ||'\
                ' (gen_m_vis <= 60 || gen_m_vis >= 120))'
            ]
        }
    elif channel == 'mmet':
        process_selection = {
            "DY": [
                'is_dy_tt != 1',
                'genmatch_pt_1 > 25',
                'abs(genmatch_eta_1) < 2.4'
            ],
            "W": [
                'gen_match_1 != 15',
                'genmatch_pt_1 > 25',
                'abs(genmatch_eta_1) < 2.4'
            ],
            "TT": [],
            "VV": [],
            "ST": [],
            "VBF": [],
            "DYtau": [
                'is_dy_tt == 1'
            ],
            "Wtau": [
                'gen_match_1 == 15'
            ],
            "Wnonfid": [
                'gen_match_1 != 15',
                '((genmatch_pt_1 <= 25) || (abs(genmatch_eta_1) >= 2.4))'
            ],
            "DYnonfid": [
                'is_dy_tt != 1',
                '((genmatch_pt_1 <= 25) || (abs(genmatch_eta_1) >= 2.4))'
            ]
        }
    else:
        raise ValueError(f"Unknown channel: {channel}. Supported channels are 'mm' and 'mmet'.")
    
    return process_selection