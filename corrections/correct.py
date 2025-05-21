import correction_setup.parser as parser
import correction_setup.logger as logger
import correction_setup.config as config
import logging
# import correction_setup.correction_handler as correction_handler

# from src import correction_handler


def main():
    args = parser.setup()

    main_logger = logger.setup('main.log', args.debug)

    # get the corrections that shall be computed
    corrections = [key for key, value in vars(args).items() if value]

    main_logger.info(
        f"Starting the main correction handler with options {corrections}. "\
        f"and for files in path: {config.inpath}."
    )

    if args.pileup:
        from src.pileup.pileup_correction import PileupCorrection
        correction_handler = PileupCorrection(
            inpath=config.inpath,
            correction='pu',
            args = args
        )
        main_logger.info("Applying pileup correction.")
        correction_handler.run()

    if args.bosonpt:
        from src.bosonpt.bosonpt_correction import BosonPtCorrection
        correction_handler = BosonPtCorrection(
            inpath=config.inpath,
            correction='ptweight',
            args = args
        )
        main_logger.info("Applying boson pT correction.")
        correction_handler.run()

    if args.sf:
        from src.scalefactors.scalefactor_correction import ScaleFactorCorrection
        correction_handler = ScaleFactorCorrection(
            inpath=config.inpath,
            correction='sf',
            args = args
        )
        main_logger.info("Applying scale factor correction.")
        correction_handler.prepare()
        correction_handler.run()
        # correction_handler.apply_sf_correction()

    if args.xy:
        from src.metxy.metxy_correction import METXYCorrection
        correction_handler = METXYCorrection(
            inpath=config.inpath,
            correction='metxy',
            args = args
        )
        main_logger.info("Applying MET xy correction.")
        correction_handler.prepare()
        correction_handler.run()
        # correction_handler.apply_xy_correction()

    if args.scare:
        from src.scare.muonpt_correction import MuonPtCorrection
        correction_handler = MuonPtCorrection(
            inpath=config.inpath,
            correction='lepton',
            args = args
        )
        main_logger.info("Applying muon scale and resolution correction.")

        correction_handler.prepare()
        correction_handler.run()

    if args.recoil:
        main_logger.info("Applying recoil correction.")
        # correction_handler.apply_recoil_correction()

    if args.qcd:
        main_logger.info("Applying QCD estimation.")
        # correction_handler.apply_qcd_correction()

    main_logger.info("Script finished.")

    


if __name__ == "__main__":
    main()