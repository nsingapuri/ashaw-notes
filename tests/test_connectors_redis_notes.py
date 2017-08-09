""" Testing Local Notes Module
"""

import unittest
from connectors import redis_notes
from mock import MagicMock, patch
from ddt import ddt, data, unpack


@ddt
class LocalNotesTests(unittest.TestCase):
    """Unit Testing Local Notes"""

    @unpack
    @data(
        ('redis_notes', True),
        ('redis_notes, local_notes', True),
        ('local_notes', False),
    )
    @patch('utils.configuration.load_config')
    def test_is_enabled(self, string, expectation, load_config):
        """Verifies is_enabled is properly functioning"""

        mock_config = MagicMock()
        mock_config.get.return_value = string
        load_config.return_value = mock_config

        self.assertEqual(expectation, redis_notes.is_enabled())


    @patch('connectors.redis_notes.add_redis_note')
    def test_save_note(self, add_redis_note):
        """Verifies save_note is properly functioning"""
        redis_notes.save_note(12345, "test note")
        add_redis_note.assert_called_once_with(12345, "test note")
    
    @patch('connectors.redis_notes.delete_redis_note')
    def test_delete_note(self, delete_redis_note):
        """Verifies delete_note is properly functioning"""
        redis_notes.delete_note(12345)
        delete_redis_note.assert_called_once_with(12345)


    @patch('connectors.redis_notes.save_note')
    @patch('connectors.redis_notes.delete_redis_note')
    def test_update_note(self, delete_redis_note, save_note):
        """Verifies update_note is properly functioning"""
        redis_notes.update_note(12345, 23456, "test note")
        delete_redis_note.assert_called_once_with(12345)
        save_note.assert_called_once_with(23456, "test note")
    
    
    @patch('utils.search.get_search_request')
    @patch('connectors.redis_notes.find_redis_notes')
    def test_find_notes(self, find_redis_notes, get_search_request):
        """Verifies update_note is properly functioning"""
        redis_notes.find_notes(["test note"])
        get_search_request.assert_called_once_with(["test note"])
        find_redis_notes.assert_called_once()

    @unpack
    @data(
        (1373500800, 'note_1373500800'),
        (1450794188, 'note_1450794188'),
        ('*', 'note_*'),
    )
    def test_get_note_key(self, timestamp, expectation):
        """Verifies get_note_key is properly functioning"""
        key = redis_notes.get_note_key(timestamp)
        self.assertEqual(expectation, key)

    @unpack
    @data(
        ('test', 'w_test'),
        ('test1234', 'w_test1234'),
        ('#hashtag', 'w_#hashtag'),
        ('*', 'w_*'),
    )
    def test_get_word_key(self, word, expectation):
        """Verifies get_word_key is properly functioning"""
        key = redis_notes.get_word_key(word)
        self.assertEqual(expectation, key)

    @unpack
    @data(
        (1373500800, "a quick note", [
            'w_a',
            'w_quick',
            'w_note',
            'year_2013',
            'month_7',
            'day_11',
            'hour_0',
            'weekday_3']),
        (1373500800, "a a a quick note", [
            'w_a',
            'w_quick',
            'w_note',
            'year_2013',
            'month_7',
            'day_11',
            'hour_0',
            'weekday_3']),
        (1373500800, "special&&& characters #awesome", [
            'w_special',
            'w_characters',
            'w_awesome',
            'w_#awesome',
            'year_2013',
            'month_7',
            'day_11',
            'hour_0',
            'weekday_3']),
        (1450794188, "#yolo #sl4life #tons-of-hashtags #yolo", [
            'w_yolo',
            'w_sl4life',
            'w_tons',
            'w_of',
            'w_hashtags',
            'w_#yolo',
            'w_#sl4life',
            'w_#tons-of-hashtags',
            'year_2015',
            'month_12',
            'day_22',
            'hour_14',
            'weekday_1']),
    )
    def test_get_note_tokens(self, timestamp, note, expectation):
        """Verifies get_note_tokens is properly functioning"""
        tokens = redis_notes.get_note_tokens(timestamp, note)
        self.assertListEqual(expectation, tokens)
