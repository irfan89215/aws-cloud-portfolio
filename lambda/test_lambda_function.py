"""Unit tests for the visitor counter Lambda function.

boto3 is patched, so no AWS account, credentials, or network are needed.
"""
import json
import sys
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


def load_function(table):
    """Import lambda_function with a fake DynamoDB table in place of the real one."""
    fake_resource = MagicMock()
    fake_resource.Table.return_value = table
    sys.modules.pop("lambda_function", None)
    with patch("boto3.resource", return_value=fake_resource):
        import lambda_function
    return lambda_function


def make_table(visits=5):
    table = MagicMock()
    # DynamoDB returns numbers as Decimal
    table.update_item.return_value = {"Attributes": {"visits": Decimal(visits)}}
    return table


def test_returns_200_and_the_new_count():
    module = load_function(make_table(visits=12))

    response = module.lambda_handler({}, None)

    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"
    assert json.loads(response["body"]) == {"count": 12}


def test_increments_one_item_atomically():
    table = make_table()
    module = load_function(table)

    module.lambda_handler({}, None)

    table.update_item.assert_called_once()
    kwargs = table.update_item.call_args.kwargs
    assert kwargs["Key"] == {"id": "site"}
    assert kwargs["UpdateExpression"] == "ADD visits :inc"
    assert kwargs["ExpressionAttributeValues"] == {":inc": 1}


def test_uses_the_visitor_counter_table():
    fake_resource = MagicMock()
    fake_resource.Table.return_value = make_table()
    sys.modules.pop("lambda_function", None)
    with patch("boto3.resource", return_value=fake_resource):
        import lambda_function  # noqa: F401

    fake_resource.Table.assert_called_once_with("visitor-counter")


def test_database_errors_are_not_swallowed():
    """An unhandled error must reach Lambda so the Errors metric and alarm fire."""
    table = make_table()
    table.update_item.side_effect = RuntimeError("DynamoDB unavailable")
    module = load_function(table)

    with pytest.raises(RuntimeError):
        module.lambda_handler({}, None)
