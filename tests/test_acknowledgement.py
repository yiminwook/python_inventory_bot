import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class AcknowledgementTests(unittest.TestCase):
    def setUp(self):
        config = types.ModuleType("src.config")
        config.CHAT_ID = "123"
        config.PURCHASE_PAGE_URL = "https://example.com"
        telegram = types.ModuleType("src.telegram_util")
        telegram.send_telegram_message = Mock()
        telegram.get_latest_telegram_message = Mock()
        selenium = types.ModuleType("src.selenium_util")
        selenium.get_page_content = Mock()
        util = types.ModuleType("src.util")
        util.time_print = Mock()
        with patch.dict(sys.modules, {
            "src.config": config, "src.telegram_util": telegram,
            "src.selenium_util": selenium, "src.util": util,
        }):
            spec = importlib.util.spec_from_file_location(
                "inventory_main", Path(__file__).resolve().parents[1] / "main.py"
            )
            self.bot = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.bot)
        self.bot.alert_active = True
        self.bot.last_update_id = 10

    def message(self, update_id, text, chat_id=123):
        return {"update_id": update_id, "message": {
            "chat": {"id": chat_id}, "text": text,
        }}

    def test_acknowledgement_before_another_message(self):
        self.bot.get_latest_telegram_message.return_value = {"result": [
            self.message(10, "확인함"), self.message(11, "다음 메시지"),
        ]}
        self.bot.alert_until_acknowledged()
        self.assertFalse(self.bot.alert_active)
        self.assertTrue(self.bot.terminate_program)
        self.bot.send_telegram_message.assert_called_once_with(
            "확인하였습니다. 프로그램을 종료합니다."
        )

    def test_ignores_other_chats_and_non_text_updates_and_advances_offset(self):
        self.bot.get_latest_telegram_message.side_effect = [
            {"result": [self.message(10, "확인함", 999),
                        {"update_id": 11, "message": {"photo": []}},
                        {"update_id": 12, "callback_query": {}}]},
            {"result": [self.message(13, "확인 함")]},
        ]
        with patch.object(self.bot.time, "sleep"):
            self.bot.alert_until_acknowledged()
        self.assertEqual(self.bot.last_update_id, 14)
        self.assertEqual(self.bot.get_latest_telegram_message.call_args_list[1].args, (13,))
        self.assertTrue(self.bot.terminate_program)

    def test_recovers_from_receive_failure(self):
        self.bot.get_latest_telegram_message.side_effect = [
            RuntimeError("temporary failure"),
            {"result": [self.message(10, "확인함")]},
        ]
        with patch.object(self.bot.time, "sleep"):
            self.bot.alert_until_acknowledged()
        self.assertTrue(self.bot.terminate_program)


if __name__ == "__main__":
    unittest.main()
