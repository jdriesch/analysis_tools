from src.hist_manager import ProcessManager
from src.plot_manager import PlotManager
from plot_setup.binnings import histo
from plot_setup.samples import get_samples
import plot_setup.selections as selections
import plot_setup.logger as logger

main_logger = logger.setup('main.log', True)
main_logger.info(
    f"Starting the histogram handler. "
)

do_hists = False

if do_hists == 'True':
    samples = get_samples('mm')

    base_selection = selections.get_base_selection('mm')
    base_selection, add_selection = selections.update_selection(base_selection)
    process_selection = selections.get_process_selection('mm')

    process_manager = ProcessManager(
        files=samples,
        filters={
            "base": base_selection,
            "process": process_selection,
            "add": add_selection
        },
        categories=['EWK', 'DY', 'TT', 'Data'],
        binnings=histo,
        friends=['sf', 'xy', 'pu', 'ptweight', 'xsec', 'xy'],
        save_path='output/root/test.root',
    )

    process_manager.run_local()


else:
    plot_manager = PlotManager(
        loadpath='output/root/test.root',
        savepath='output/pdf/test.pdf')