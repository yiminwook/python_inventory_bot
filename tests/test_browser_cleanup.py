import signal
import unittest
from unittest.mock import Mock, patch

from src import browser_cleanup


def process(pid, parent, command, uid=1000):
    entry = Mock()
    entry.name = str(pid)
    entry.stat.return_value.st_uid = uid
    cmdline = Mock()
    cmdline.read_bytes.return_value = command.encode() + b'\0'
    stat = Mock()
    # Fields following comm start at field 3; starttime is field 22.
    stat.read_text.return_value = f'{pid} (chrome worker) S {parent} ' + '0 ' * 17 + '123'
    entry.__truediv__ = Mock(side_effect=lambda name: cmdline if name == 'cmdline' else stat)
    return entry


class BrowserCleanupTests(unittest.TestCase):
    def test_only_project_driver_and_its_descendants_are_selected(self):
        entries = [process(10, 1, '/project/chromedriver'),
                   process(11, 10, '/opt/google/chrome/chrome'),
                   process(12, 11, '/opt/google/chrome/chrome'),
                   process(20, 1, '/other/chromedriver'),
                   process(21, 20, '/opt/google/chrome/chrome'),
                   process(30, 1, '/project/chromedriver', uid=2000)]
        with patch.object(browser_cleanup, 'Path') as path, \
                patch.object(browser_cleanup.os, 'getuid', return_value=1000, create=True):
            path.return_value.glob.return_value = entries
            targets = browser_cleanup.find_browser_processes('/project/chromedriver')
        self.assertEqual(set(targets), {10, 11, 12})

    def test_reused_pid_is_not_killed(self):
        with patch.object(browser_cleanup, 'Path') as path, \
                patch.object(browser_cleanup.os, 'kill') as kill:
            path.return_value.read_text.return_value = '10 (chrome) S 1 ' + '0 ' * 17 + '456'
            browser_cleanup.signal_processes({10: '123'}, signal.SIGTERM)
        kill.assert_not_called()


if __name__ == '__main__':
    unittest.main()
