import numpy as np

def get_base_selection(region, postfix):
    
    # Get the Z region selection
    if region=='Z':
        acceptance = (
            f"( pt_1{postfix}>25. && pt_2{postfix}>25. && "
            "abs(eta_1) < 2.4 && abs(eta_2) < 2.4)"
        )
        id = "(tightId_1 && tightId_2)"
        iso = "(iso_1 < 0.15 && iso_2 < 0.15)"
        trg = "(trg_single_mu24_1 || trg_single_mu24_2)"
        add = (
            f"(q_1*q_2 < 0) &&"
            f"(m_vis{postfix} > 60. && m_vis{postfix} < 120.)"
            # "(pog_puweight < 100)"
        )

    # Get the Wplus or Wminus region selection
    elif region in ['Wp', 'Wm']:
        acceptance = f"(pt_1{postfix}>25. && abs(eta_1) < 2.4)"
        id = "(tightId_1) && (extramuon_veto == 1)"
        iso = "(iso_1 < 0.15)"
        trg = "(trg_single_mu24_1)"

        if region == 'Wp':
            add = "(q_1 > 0)"
        elif region == 'Wm':
            add = "(q_1 < 0)"
    
    region_selection = {
        'acceptance': acceptance,
        'id': id,
        'iso': iso,
        'trg': trg,
        'add': add
    }

    return region_selection


def get_region_selections(args):
    all_selections = {}

    # standard acceptance variations to be applied across all regions
    variations = []

    if not args.noNom:
        variations.append("Nominal")
    
    if not args.noPtVar:
        variations += ["scaleup", "scaledn", "resolup", "resoldn"]

    for region in ["Z", "Wp", "Wm"]:
        all_selections[region] = {}

        for var in variations:
            postfix = "_corr"
            if "scale" in var or "resol" in var:
                postfix += "_" + var
            all_selections[region][var] = get_base_selection(
                region, postfix
            )

    # isolation variation for QCD extrapolation (only in W region)
    if not args.noIso:
        iso_values = [round(n, 3) for n in np.arange(0.2, 1.01, 0.05)]
        n_isobins = len(iso_values) - 1

        for region in ["Wp", "Wm"]:
            for i in range(n_isobins):
                postfix = "_corr"
                variation = f"(iso_1 > {iso_values[i]} && iso_1 < {iso_values[i+1]})"
                var = f'iso_bin_{i+5}'
                all_selections[region][var] = get_base_selection(region, postfix)
                all_selections[region][var]["iso"] = variation
    
    return all_selections


def get_region_categories(region):
    if region == 'Z':
        categories = {
            'signal': ['DY'],
            'background': ['EWK', 'TT'], 
            'data': ['Data']
        }
    elif region in ['Wp', 'Wm']:
        categories = {
            'signal': [region, 'DY', f'QCD{region}'],
            'background': ['EWK', 'TT'],
            'data': ['Data']
        }
    else:
        raise ValueError(
            f"Unknown region: {region}. "\
            "Supported regions are 'Z', 'Wp', and 'Wm'."
        )
    
    return categories


def get_process_selection(region):
    """
    Get the process selection for the analysis.
    """
    if region == 'Z':
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
        
    elif region == 'Wp' or region == 'Wm':
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
            region: {region: w},
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
            f"Unknown region: {region}. "\
            "Supported regions are 'Z', 'Wp', and 'Wm'."
        )

    return process_selection