import logging


def setup_logging():
    """
    Configures the logging system to log to both a file and the console.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bybit_connector.log"),
            logging.StreamHandler(),
        ],
    )
