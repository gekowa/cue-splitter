# argparse and optional filename checks

## Intent
Allow users to process audio whose names fail the existing filename heuristic, without changing `valid_filename`.

## Goals and constraints
- Replace manual `sys.argv` parsing in `split.py` with standard-library `argparse`.
- Keep the required positional `directory` argument and add standard `-h` / `--help` behavior. Help must explain recursive directory processing, strict-by-default filename checks, both effects of the bypass flag, and show a usage example; it must exit without processing files.
- Add `--skip-filename-check`, disabled by default.
- When enabled, short-circuit both `valid_filename` conditions: directory eligibility and post-split deletion.
- Preserve `valid_filename` unchanged and retain all other processing and deletion conditions.
- No new dependencies, global configuration, or unrelated refactoring.

## Approaches
1. Bypass both filename checks: accepts previously rejected directory contents and allows cleanup of original audio irrespective of its filename. This also expands deletion eligibility.
2. Bypass directory selection only: accepts more directories but retains the filename restriction on cleanup, potentially retaining original audio.

The user selected **both checks**. This keeps the bypass consistent across processing and cleanup.

## Implementation decisions
- Pass `skip_filename_check=False` through `traverse_directories`, `process_directory`, and `handle_size_increase`; the CLI supplies the parsed boolean.
- Use `(skip_filename_check or valid_filename(file))` at each existing check, so the function is not called when the flag is set.
- Keep existing script and container invocations working; document the new flag and its deletion implications in `README.md`.
- Add one small runnable regression check covering strict and relaxed processing and cleanup. Exercise the CLI help, argument errors, and both modes against disposable audio.

## Usage
```sh
python split.py <directory>
python split.py --skip-filename-check <directory>
python split.py --help
```

## Non-goals and remaining choices
Do not change filename rules, conversion, splitting, interruption handling, or cleanup thresholds. Test setup details remain an implementation choice.
