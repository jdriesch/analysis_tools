def get_weights(proc, variation=''):
    """
    Get the weights only if the postfix is empty.
    """
    if proc == 'Data':
        return {'Nominal': '1.0'}

    baseweight = 'genweight*sumwWeight*crossSectionPerEventWeight'
    evtweight = '*pog_puweight*ptweight*5010'

    if 'iso' in variation:
        sfweight = '*sf_trk*sf_sta*sf_id*sf_highiso_iso*sf_highiso_trg*sf_prefire'
    else:
        sfweight = '*sf_trk*sf_sta*sf_id*sf_iso*sf_trg*sf_prefire'

    nominal = baseweight+evtweight+sfweight

    weight_variations = {
        'Nominal': nominal
    }

    if variation != 'Nominal':
        return weight_variations

    # variations of efficiency scale factors
    for var in sfweight.split('*')[1:]:
        weight_variations[var+'Up'] = nominal.replace(var, var+'_up')
        weight_variations[var+'Down'] = nominal.replace(var, var+'_dn')

    # variations of pileup and pt weights
    for var in ['pog_puweight', 'ptweight']:
        weight_variations[var+'Up'] = nominal.replace(var, var+'Up')
        weight_variations[var+'Down'] = nominal.replace(var, var+'Dn')

    if proc in ['VV', 'VBF']:
        return weight_variations
    
    # variations of pdfs
    for i in range(1, 101):
        weight_variations[f'LHEPdfWeight{i}Up'] = nominal+f'*LHEPdfWeight{i}'
        weight_variations[f'LHEPdfWeight{i}Down'] = nominal+f'*(2.-LHEPdfWeight{i})'

    # variations of scales
    weight_variations['LHEPdfWeightAlphaSUp'] = nominal+'*LHEPdfWeight102'
    weight_variations['LHEPdfWeightAlphaSDown'] = nominal+'*LHEPdfWeight101'
    weight_variations['LHEScaleWeightMUFUp'] = nominal+'*LHEScaleWeight4'
    weight_variations['LHEScaleWeightMUFDown'] = nominal+'*LHEScaleWeight3'
    weight_variations['LHEScaleWeightMURUp'] = nominal+'*LHEScaleWeight6'
    weight_variations['LHEScaleWeightMURDown'] = nominal+'*LHEScaleWeight1'
    weight_variations['LHEScaleWeightMUFMURUp'] = nominal+'*LHEScaleWeight7'
    weight_variations['LHEScaleWeightMUFMURDown'] = nominal+'*LHEScaleWeight0'

    # parton shower variations
    weight_variations['PSWeightISRUp'] = nominal+'*PSWeight0'
    weight_variations['PSWeightISRDown'] = nominal+'*PSWeight2'
    weight_variations['PSWeightFSRUp'] = nominal+'*PSWeight1'
    weight_variations['PSWeightFSRDown'] = nominal+'*PSWeight3'

    return weight_variations