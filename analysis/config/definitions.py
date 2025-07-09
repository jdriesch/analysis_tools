def get_definitions(variation):
    """
    Get the definitions for the analysis.
    """

    postfix = '_corr'

    if 'scale' in variation or 'resol' in variation:
        postfix += '_' + variation
    
    definitions = {
        'pfmt'+postfix: f'sqrt(2 * pfmet{postfix} * pt_1{postfix} * (1 - cos(phi_1 - pfmetphi{postfix})))',
    }
    
    return definitions