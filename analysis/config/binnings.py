def get_histograms(region, variation=''):
    """
    Get the histograms for the analysis.
    """

    postfix = '_corr'

    if 'scale' in variation or 'resol' in variation:
        postfix += '_' + variation

    histo_mmet = {
        'pfmt'+postfix: {
            'xtitle': 'm_{T} (GeV)',
            'ytitle': 'Events',
            'bins': [20, 0, 120],
            'overflow': True,
        },
    }

    histo_mm = {
        'm_vis'+postfix: {
            'xtitle': 'm_{#mu#mu} (GeV)',
            'ytitle': 'Events',
            'bins': [30, 60, 120],
            'overflow': False
        },  
    }

    if region == 'Z':
        return histo_mm

    elif region in ['Wp', 'Wm']:
        return histo_mmet
    else:
        raise ValueError(f"Unknown region: {region}")
    