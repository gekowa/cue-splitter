from pathlib import Path
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory
from unittest.mock import patch

import split


def test_filename_check_bypass():
    """The bypass changes eligibility and cleanup, not other deletion guards."""
    def run_audio_tool(command, **kwargs):
        if command[0] == 'ffprobe':
            return CompletedProcess(command, 0, stdout='44100\n1411200\n')
        assert command[0] == 'split2flac'
        Path('(01) [Artist] First.flac').write_bytes(b'a' * 50)
        Path('(02) [Artist] Second.flac').write_bytes(b'b' * 50)
        return CompletedProcess(command, 0)

    with TemporaryDirectory() as directory:
        album = Path(directory) / 'nested album'
        album.mkdir()
        source = album / '01.flac'
        source.write_bytes(b'x' * 100)
        notes = album / 'notes.txt'
        notes.write_bytes(b'n' * 200)

        with patch('split.subprocess.run', side_effect=run_audio_tool):
            split.traverse_directories(directory)
            assert {p.name for p in album.iterdir()} == {'01.flac', 'notes.txt'}

            with patch('split.valid_filename', side_effect=AssertionError('Filename check was not skipped')):
                split.traverse_directories(directory, skip_filename_check=True)

        assert {p.name for p in album.iterdir()} == {
            '(01) [Artist] First.flac', '(02) [Artist] Second.flac', 'notes.txt'
        }
        assert notes.read_bytes() == b'n' * 200

        source.write_bytes(b'x' * 100)
        split.handle_size_increase(album, initial_size=100)
        assert source.read_bytes() == b'x' * 100

        split.handle_size_increase(album, initial_size=200, skip_filename_check=True)
        assert source.read_bytes() == b'x' * 100


if __name__ == '__main__':
    test_filename_check_bypass()
    print('Filename-check bypass regression passed.')
