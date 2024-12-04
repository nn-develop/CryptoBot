import requests
import csv
from datetime import datetime


class BybitConnector:
    """
    Connector to fetch historical price data from the Bybit API.

    This class handles fetching price data for a specific cryptocurrency symbol
    within a given time range and interval, using the Bybit public API. It provides
    methods to retrieve data and save it to a CSV file.
    """

    PRICE_API_URL = "https://api.bybit.com/v5/market/kline"

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
        dt: datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())

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
        batch_start = start_timestamp

        while batch_start < end_timestamp:
            max_batch_end: int = batch_start + (limit * seconds_per_candle)
            batch_end: int = min(max_batch_end, end_timestamp)
            candles_limit: int = (batch_end - batch_start) // seconds_per_candle

            params = {
                "category": self.category,
                "symbol": self.symbol,
                "interval": self.interval,
                "start": batch_start,
                "limit": candles_limit,
            }

            response: requests.Response = requests.get(
                self.PRICE_API_URL, params=params
            )
            response_data: dict = response.json()

            if response.status_code != 200 or response_data.get("retCode") != 0:
                raise ValueError(f"API error: {response_data.get('retMsg')}")

            candles: list[list[str]] = response_data.get("result", {}).get("list", [])

            if not candles:
                break
            all_candles.extend(candles)
            batch_start: int = batch_end

        return all_candles

    def save_to_csv(self, candles: list[list[str]]):
        """
        Saves the fetched candlestick data to a CSV file.

        The file is named based on the symbol, interval, and date range. The columns in the CSV file are:
        timestamp, open, high, low, close, and volume.

        Args:
            candles (list[list[str]]): The list of candlestick data to be saved.
        """
        filename: str = f"{self.symbol}_{self.interval}_{self.start}_{self.end}.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])

            for candle in candles:
                writer.writerow(candle)

        print(f"Data has been saved to {filename}")


# Example usage
if __name__ == "__main__":
    # Only pass the parameters once during initialization
    connector = BybitConnector(
        category="inverse",
        symbol="BTCUSD",
        interval="D",
        start="2022-04-01 00:00:00",
        end="2024-12-03 00:00:00",
    )

    candles: list[list[str]] = connector.get_prices()

    # Save the result to CSV
    connector.save_to_csv(candles)
