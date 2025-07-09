from main_setup.parser import parse_args
import main_setup.logger as setup_logger
from pipeline import run_pipeline


if __name__ == '__main__':
    args = parse_args()
    logger = setup_logger.setup('main.log', args.debug)


    run_pipeline(args)