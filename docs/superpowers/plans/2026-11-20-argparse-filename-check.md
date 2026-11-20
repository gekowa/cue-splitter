# Filename-check CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add argparse usage help and an opt-in bypass of both existing filename checks.

**Architecture:** Keep parsing in the existing script entrypoint. Pass one default-false boolean through the existing traversal, processing, and cleanup functions; do not alter `valid_filename`.

**Tech Stack:** Python standard-library argparse and unittest.mock; existing audio dependencies unchanged.

**Spec:** `docs/superpowers/specs/2026-11-20-argparse-filename-check-design.md`

## Global Constraints
- Required positional `directory`; `-h` / `--help` exits without processing files.
- `--skip-filename-check` bypasses both checks; default behavior stays strict.
- Preserve `valid_filename` unchanged and retain all other processing and deletion conditions.
- No new dependencies, global configuration, or unrelated refactoring.

## Review Focus
- Missing directory and unknown options must fail parsing without processing.
- Help must work without a directory and explain bypass-related deletion.
- A filename rejected by default must become eligible in relaxed mode, including nested directories.
- Relaxed cleanup must still protect non-audio and below-average-size files.
- Relaxed cleanup must still require the existing 1.5x size-increase threshold.

### Task 1: CLI and filename bypass

**Files:** Modify `split.py` and `README.md`; create `test_split.py` for one standalone regression check.

**Interfaces:** Add `skip_filename_check=False` to `traverse_directories`, `process_directory`, and `handle_size_increase`. Pass the boolean through all existing calls. CLI uses `argparse.ArgumentParser` and `store_true`.

- [x] Write one regression scenario that exercises actual filesystem effects with disposable files, substituting only external audio work: strict mode leaves a rejected source untouched; relaxed mode processes it and removes the oversized original while preserving split tracks and non-audio files. Check cleanup with no size growth.
- [x] Run `python3 test_split.py`; expect failure because the optional bypass is absent. Probe `python3 split.py --help` before the change to establish missing help behavior.
- [x] Add the parser with help text and an example; change only the three signatures, their calls, and the two conditions to `(skip_filename_check or valid_filename(file))`.
- [x] Run `python3 test_split.py`; expect the regression scenario to pass. Smoke the real CLI with help, missing and unknown arguments, strict and relaxed directory processing, a nested directory, and disposable real audio where dependencies are available.
- [x] Document direct Python usage, help, the bypass, and deletion implications in `README.md`.

Execution is inline in the current workspace. No new test framework or product abstractions are needed.

## Verification record
- Standalone regression: failed before implementation on the absent parameter; passed afterward.
- CLI: `-h` and `--help` exited successfully; missing directory and unknown options exited with code 2. Both option orders worked with a directory containing spaces.
- Audio smoke: strict mode preserved the rejected source; relaxed mode processed a nested album, backed up its CUE, deleted the original, and retained two one-second FLAC tracks. FFmpeg and ffprobe were real; unavailable `split2flac` was replaced by a temporary FFmpeg-backed executable.
- Existing pinned Python dependencies were installed only in a temporary virtual environment. No dependency files changed.
- Follow-up Docker verification supersedes the host-only integration limitation: ran the current `split.py` mounted read-only into the existing `linux/amd64` image, with its real `split2flac` executable (SHA-256 identical to the repository copy). Default `CMD` preserved a rejected filename; the explicit wrapper with `--skip-filename-check` split a nested album into two tagged one-second FLAC tracks, backed up the CUE, and deleted the original. Docker help, argument-error cases, and the standalone regression also passed. No image was rebuilt or published.
