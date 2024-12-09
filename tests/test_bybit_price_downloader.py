import unittest
import responses
import requests
from datetime import datetime
from src.bybit_price_downloader import (
    BybitConnector,
)


class TestBybitConnector(unittest.TestCase):
    """
    Test suite for the BybitConnector class, which interacts with the Bybit API to fetch price data.
    """

    @responses.activate
    def test_get_prices_success(self):
        """
        Test if get_prices() correctly parses and returns data when the API response is successful.
        """
        mock_response = {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "list": [
                    [1609459200, "35000", "36000", "34000", "35500", "100", "500000"],
                    [1609462800, "35500", "36500", "34500", "36000", "200", "700000"],
                ]
            },
        }
        responses.add(
            responses.GET,
            "https://api.bybit.com/v5/market/kline",
            json=mock_response,
            status=200,
        )

        connector = BybitConnector(
            category="inverse",
            symbol="BTCUSD",
            interval="D",
            start="2024-12-01 00:00:00",
            end="2024-12-02 00:00:00",
        )

        # Act
        candles = connector.get_prices()

        # Assert
        self.assertEqual(
            len(candles), 2, "The number of candles should match the mock response."
        )
        self.assertEqual(
            candles[0],
            [1609459200, "35000", "36000", "34000", "35500", "100", "500000"],
            "The first candle should match the first element of the mock response.",
        )
        self.assertEqual(
            candles[1],
            [1609462800, "35500", "36500", "34500", "36000", "200", "700000"],
            "The second candle should match the second element of the mock response.",
        )

    @responses.activate
    def test_get_prices_api_error(self):
        """
        Test if get_prices() raises a ValueError when the API response indicates an error.
        """
        mock_response = {"retCode": 10001, "retMsg": "API error"}
        responses.add(
            responses.GET,
            "https://api.bybit.com/v5/market/kline",
            json=mock_response,
            status=200,
        )

        connector = BybitConnector(
            category="inverse",
            symbol="BTCUSD",
            interval="D",
            start="2024-12-01 00:00:00",
            end="2024-12-02 00:00:00",
        )

        # Act and Assert
        with self.assertRaises(ValueError) as context:
            connector.get_prices()

        self.assertIn(
            "API error: API error",
            str(context.exception),
            "Exception message should include the API error.",
        )

    @responses.activate
    def test_get_prices_http_request_failure(self):
        """
        Test if get_prices() raises a RequestException when an HTTP request fails.
        """
        responses.add(
            responses.GET,
            "https://api.bybit.com/v5/market/kline",
            body="Server Error",
            status=500,
        )

        connector = BybitConnector(
            category="inverse",
            symbol="BTCUSD",
            interval="D",
            start="2024-12-01 00:00:00",
            end="2024-12-02 00:00:00",
        )

        # Act and Assert
        with self.assertRaises(requests.RequestException):
            connector.get_prices()

    @responses.activate
    def test_get_prices_invalid_date_format(self):
        """
        Test if get_prices() raises a ValueError for invalid date formats.
        """
        connector = BybitConnector(
            category="inverse",
            symbol="BTCUSD",
            interval="D",
            start="2024-12-01 25:00:00",  # Invalid hour
            end="2024-12-02 00:00:00",
        )

        # Act and Assert
        with self.assertRaises(ValueError):
            connector.get_prices()

    @responses.activate
    def test_get_prices_empty_result(self):
        """
        Test if get_prices() returns an empty list when the API response contains no data.
        """
        mock_response = {"retCode": 0, "retMsg": "OK", "result": {"list": []}}
        responses.add(
            responses.GET,
            "https://api.bybit.com/v5/market/kline",
            json=mock_response,
            status=200,
        )

        connector = BybitConnector(
            category="inverse",
            symbol="BTCUSD",
            interval="D",
            start="2024-12-01 00:00:00",
            end="2024-12-02 00:00:00",
        )

        # Act
        candles = connector.get_prices()

        # Assert
        self.assertEqual(
            candles,
            [],
            "The result should be an empty list when the API returns no data.",
        )


if __name__ == "__main__":
    unittest.main()
