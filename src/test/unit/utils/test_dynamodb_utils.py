import unittest
from unittest.mock import patch, MagicMock
from strategies.utils.dynamodb_utils import DynamoDBUtils


class TestDynamoDBUtils(unittest.TestCase):
    def setUp(self):
        # Patch boto3.resource used inside DynamoDBClient to avoid real AWS calls
        patcher = patch('boto3.resource')
        self.addCleanup(patcher.stop)
        self.mock_resource = patcher.start()

        # Mock the Table returned by boto3.resource
        self.mock_table = MagicMock()
        self.mock_resource.return_value.Table.return_value = self.mock_table

        # Instantiate DynamoDBUtils (inherits from DynamoDBClient)
        self.dynamodb_utils = DynamoDBUtils()

    @patch.object(DynamoDBUtils, 'get_item')
    def test_fetch_item_by_key_success(self, mock_get_item):
        mock_get_item.return_value = {'Item': {'id': '1'}}
        result = self.dynamodb_utils.fetch_item_by_key('table', {'id': '1'})
        self.assertEqual(result, {'Item': {'id': '1'}})
        mock_get_item.assert_called_once_with('table', {'id': '1'})

    @patch.object(DynamoDBUtils, 'get_item')
    def test_fetch_item_by_key_error(self, mock_get_item):
        mock_get_item.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.fetch_item_by_key('table', {'id': '1'})
        mock_get_item.assert_called_once_with('table', {'id': '1'})

    def test_save_item_success(self):
        self.mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        result = self.dynamodb_utils.save_item('table', {'id': '1'})
        self.assertEqual(result, {'ResponseMetadata': {'HTTPStatusCode': 200}})
        self.mock_table.put_item.assert_called_once()

    def test_save_item_error(self):
        self.mock_table.put_item.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.save_item('table', {'id': '1'})
        self.mock_table.put_item.assert_called_once()

    def test_update_item_attributes_success(self):
        self.mock_table.update_item.return_value = {'Attributes': {'attr': 'val'}}
        result = self.dynamodb_utils.update_item_attributes('table', {'id': '1'}, 'SET attr = :val', {':val': 'val'})
        self.assertEqual(result, {'Attributes': {'attr': 'val'}})
        self.mock_table.update_item.assert_called_once()

    def test_update_item_attributes_error(self):
        self.mock_table.update_item.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.update_item_attributes('table', {'id': '1'}, 'SET attr = :val', {':val': 'val'})
        self.mock_table.update_item.assert_called_once()

    def test_remove_item_by_key_success(self):
        self.mock_table.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        result = self.dynamodb_utils.remove_item_by_key('table', {'id': '1'})
        self.assertEqual(result, {'ResponseMetadata': {'HTTPStatusCode': 200}})
        self.mock_table.delete_item.assert_called_once()

    def test_remove_item_by_key_error(self):
        self.mock_table.delete_item.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.remove_item_by_key('table', {'id': '1'})
        self.mock_table.delete_item.assert_called_once()

    def test_scan_all_items_with_filter_success(self):
        self.mock_table.scan.return_value = {'Items': [{'id': '1'}]}
        result = self.dynamodb_utils.scan_all_items_with_filter('table')
        self.assertEqual(result, {'Items': [{'id': '1'}]})
        self.mock_table.scan.assert_called_once()

    def test_scan_all_items_with_filter_error(self):
        self.mock_table.scan.side_effect = Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.scan_all_items_with_filter('table')
        self.mock_table.scan.assert_called_once()

    def test_force_string_success(self):
        self.assertEqual(self.dynamodb_utils.force_string(123), '123')

    def test_force_string_error(self):
        class Bad:
            def __str__(self):
                raise Exception('fail')
        with self.assertRaises(Exception):
            self.dynamodb_utils.force_string(Bad())


if __name__ == '__main__':
    unittest.main()
