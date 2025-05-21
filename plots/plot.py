from src.histograms import Histogram

hist = Histogram(
    files = '/ceph/jdriesch/CROWN_samples/test/ntuples/2022/DYto*/mm/*.root',
    friends = ['metxy', 'lepton'],
    definitions = {'weight': '1'},
)


histo = [
    {
        'name': 'm_vis_corr',
        'var': 'm_vis_corr',
        'title': 'p_{T} [GeV]',
        'bins': 60,
        'xmin': 60,
        'xmax': 120,
        'xaxis': 'pt',
        'yaxis': 'Events',
        'cut': '',
        'weight': 'weight',
        'filters': ['m_vis_corr >60', 'm_vis_corr < 120']
    },
    {
        'name': 'm_vis',
        'var': 'm_vis',
        'title': '#eta',
        'bins': 60,
        'xmin': 60,
        'xmax': 120,
        'xaxis': 'eta',
        'yaxis': 'Events',
        'cut': '',
        'weight': 'weight',
        'filters': ['m_vis >60', 'm_vis < 120']
    }
]


hist.make_hists(histo)
hist.save_hists(
    outpath = 'output/root/test.root'
)
