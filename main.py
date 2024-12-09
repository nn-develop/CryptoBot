import logging
from logger import setup_logging
from bybit_price_downloader import BybitConnector

# Setup logging
setup_logging()
logger: logging.Logger = logging.getLogger(__name__)

# if __name__ == "__main__":
#     # Only pass the parameters once during initialization
#     connector = BybitConnector(
#         category="inverse",
#         symbol="BTCUSD",
#         interval="M",
#         start="2024-12-01 00:00:00",
#         end="2024-12-04 00:00:00",
#     )

#     candles: list[list[str]] = connector.get_prices()

#     # Specify the directory to save the CSV file
#     directory = "./data/raw"
#     connector.save_to_csv(candles, directory)

logger.info(f"Success")
