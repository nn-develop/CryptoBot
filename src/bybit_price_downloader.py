import os
import requests
import csv
import logging
from datetime import datetime
from src.logger import setup_logging

# Setup logging
setup_logging()
logger: logging.Logger = logging.getLogger(__name__)


class BybitConnector:
    """
    Connector to fetch historical price data from the Bybit API.

    This class handles fetching price data for a specific cryptocurrency symbol
    within a given time range and interval, using the Bybit public API. It provides
    methods to retrieve data and save it to a CSV file.
    """

    PRICE_API_URL: str = "https://api.bybit.com/v5/market/kline"

    def __init__(self, category: str, symbol: str, interval: str, start: str, end: str):
        """
        Initializes the BybitConnector object with the provided parameters.

        Args:
            category (str): The category of the market (e.g., "inverse", "linear").
            symbol (str): The trading symbol (e.g., "BTCUSD").
            interval (str): The time interval for each candlestick (e.g., "D", "1", "5").
            start (str): The start date of the historical data in the format "YYYY-MM-DD HH:MM:SS".
            end (str): The end date of the historical data in the format "YYYY-MM-DD HH:MM:SS".
        """
        self.category: str = category
        self.symbol: str = symbol
        self.interval: str = interval
        self.start: str = start
        self.end: str = end

    @staticmethod
    def _to_unix_timestamp(date_str: str) -> int:
        """
        Converts a date string to a Unix timestamp.

        Args:
            date_str (str): The date string to be converted (format: "YYYY-MM-DD HH:MM:SS").

        Returns:
            int: The corresponding Unix timestamp.
        """
        try:
            dt: datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError as e:
            logger.error(
                f"Invalid date format: {date_str}. Expected 'YYYY-MM-DD HH:MM:SS'."
            )
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD HH:MM:SS'.") from e

    @staticmethod
    def _interval_to_seconds(interval: str) -> int:
        """
        Converts a Bybit interval string to the corresponding number of seconds.

        Args:
            interval (str): The Bybit interval (e.g., "1", "5", "D").

        Returns:
            int: The number of seconds that corresponds to the given interval.
        """
        conversion: dict[str, int] = {
            "1": 60,
            "3": 180,
            "5": 300,
            "15": 900,
            "30": 1800,
            "60": 3600,
            "120": 7200,
            "240": 14400,
            "360": 21600,
            "720": 43200,
            "D": 86400,
            "W": 604800,
            "M": 2592000,
        }
        if interval not in conversion:
            logger.warning(
                f"Unknown interval '{interval}'. Defaulting to 'D' (86400 seconds)."
            )
        return conversion.get(interval, 86400)

    def get_prices(self, limit: int = 1000) -> list[list[str]]:
        """
        Fetches historical price data from the Bybit API in chunks, respecting the time range and limit.

        The function makes multiple API requests to fetch the data in batches, handling the pagination
        based on the specified time range and limit for each request.

        Args:
            limit (int): The maximum number of data points to retrieve per API request. Default is 1000.

        Returns:
            list[list[str]]: A list of candlestick data, where each candlestick is represented as a list of strings
                             (e.g., timestamp, open, high, low, close, volume).
        """
        start_timestamp: int = self._to_unix_timestamp(self.start)
        end_timestamp: int = self._to_unix_timestamp(self.end)
        seconds_per_candle: int = self._interval_to_seconds(self.interval)

        all_candles: list[list[str]] = []
        batch_start: int = start_timestamp

        while batch_start < end_timestamp:
            max_batch_end: int = batch_start + (limit * seconds_per_candle)
            batch_end: int = min(max_batch_end, end_timestamp)
            candles_limit: int = (batch_end - batch_start) // seconds_per_candle

            params: dict[str, int | str] = {
                "category": self.category,
                "symbol": self.symbol,
                "interval": self.interval,
                "start": batch_start,
                "limit": candles_limit,
            }

            try:
                response: requests.Response = requests.get(
                    self.PRICE_API_URL, params=params, timeout=10
                )
                response.raise_for_status()
                response_data = response.json()

                if response_data.get("retCode") != 0:
                    error_message = response_data.get(
                        "retMsg", "Unknown error from API."
                    )
                    logger.error(f"API returned an error: {error_message}")
                    raise ValueError(f"API error: {error_message}")

                candles: list[list[str]] = response_data.get("result", {}).get(
                    "list", []
                )

                if not candles:
                    logger.info("No more data available for the given range.")
                    break

                all_candles.extend(candles)
                batch_start: int = batch_end

            except requests.RequestException as e:
                logger.error(f"HTTP request failed: {e}")
                raise
            except Exception as e:
                logger.critical(
                    f"Unexpected error during API request: {e}", exc_info=True
                )
                raise

        logger.info(f"Fetched {len(all_candles)} candlesticks.")
        return all_candles

    def save_to_csv(self, candles: list[list[str]], directory: str) -> None:
        """
        Saves the fetched candlestick data to a CSV file in a specified directory.

        The file is named based on the symbol, interval, and date range. The columns in the CSV file are:
        timestamp, open, high, low, close, and volume.

        Args:
            candles (list[list[str]]): The list of candlestick data to be saved.
            directory (str): The directory path where the CSV file should be saved.
        """

        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Construct the full file path
        filename: str = f"{self.symbol}_{self.interval}_{self.start}_{self.end}.csv"
        file_path: str = os.path.join(directory, filename)

        try:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["timestamp", "open", "high", "low", "close", "volume", "turnover"]
                )
                writer.writerows(candles)
            logger.info(f"Data has been saved to {file_path}.")
        except IOError as e:
            logger.error(f"Failed to write data to {file_path}: {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Only pass the parameters once during initialization
    connector = BybitConnector(
        category="inverse",
        symbol="BTCUSD",
        interval="M",
        start="2024-12-01 00:00:00",
        end="2024-12-04 00:00:00",
    )

    candles: list[list[str]] = connector.get_prices()

    # Specify the directory to save the CSV file
    directory = "./data/raw"
    connector.save_to_csv(candles, directory)
