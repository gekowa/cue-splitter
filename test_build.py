import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


def test_publish_failures():
    """A missing plugin is optional; build and actual upload failures are not."""
    root = Path(__file__).resolve().parent
    with TemporaryDirectory() as directory:
        docker = Path(directory) / 'docker'
        docker.write_text('''#!/bin/sh
case "$1 $2" in
    "help pushrm") test "$PUSHRM_INSTALLED" = 1 ;;
    # Real Docker returns success for unknown commands with --help.
    "pushrm --help") exit 0 ;;
    "context use") test "$FAIL_STAGE" != context ;;
    "buildx build") test "$FAIL_STAGE" != build ;;
    "pushrm --file") test "$PUSHRM_INSTALLED" = 1 && test "$FAIL_STAGE" != overview ;;
    *) exit 99 ;;
esac
''', encoding='utf-8')
        docker.chmod(0o755)

        failures = []
        for installed, stage in (
            ('0', ''), ('0', 'build'),
            ('1', 'context'), ('1', 'build'), ('1', 'overview'), ('1', ''),
        ):
            result = subprocess.run(
                ['/bin/sh', str(root / 'build.sh')],
                cwd=root,
                env={
                    'PATH': directory + os.pathsep + os.defpath,
                    'PUSHRM_INSTALLED': installed,
                    'FAIL_STAGE': stage,
                },
                capture_output=True,
                text=True,
                timeout=10,
            )
            if (result.returncode != 0) != bool(stage):
                failures.append(
                    f'plugin={installed}, {stage or "success"}: exit {result.returncode}\n{result.stderr}'
                )
        assert not failures, '\n'.join(failures)


if __name__ == '__main__':
    test_publish_failures()
    print('Publishing failure regression passed.')
