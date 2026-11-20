# Docker Hub Overview Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically upload README to Docker Hub after a successful image publication.

**Architecture:** Keep the existing `build.sh` publisher. Fail on build errors, then upload README after the image push if docker-pushrm is available. A missing plugin only warns and skips the overview upload.

**Tech Stack:** POSIX shell, Docker CLI, docker-pushrm; Python standard library for a standalone regression check.

**Spec:** `docs/superpowers/specs/2026-11-20-dockerhub-overview-design.md`

## Global Constraints

- Keep README as the sole source; do not rewrite its content or maintain a second overview file.
- Image contents, build platforms, tags, Docker context, audio processing, and Docker Hub's separate short description remain unchanged.
- No CI migration, automatic plugin installation, custom HTTP client, or credentials in the repository.
- Continue invoking `./build.sh` from the repository root, as the existing build command requires.
- Do not publish a real image merely to test this change.

## Review Focus

- Missing plugin: Docker accepts an unknown subcommand with `--help`; use `docker help pushrm` to detect it, warn, and skip only the overview upload.
- Failed context selection: publishing must not continue against the wrong Docker daemon.
- Failed build/push: no overview update and a nonzero exit.
- Failed overview upload: nonzero exit and a message identifying the already-pushed image.
- Successful publication: explicitly upload `README.md` to the existing repository; leave short description alone.

---

### Task 1: Failure-safe overview publishing

**Files:** Modify `build.sh`, `README.md`, and `.dockerignore`; create `test_build.py`.

**Interfaces:** `./build.sh` consumes existing Docker login and optionally docker-pushrm. It publishes `gekowa/cue-splitter:latest`, then uploads the overview when the plugin is available. Missing-plugin detection is non-blocking; context, build, and actual upload failures return nonzero.

- [x] Update `test_publish_failures()` in `test_build.py`: missing plugin plus successful build must return zero; missing plugin plus failed build must return nonzero. Keep context, build, actual upload, and fully successful cases. Model Docker's misleading unknown-subcommand `--help` success. Do not pin diagnostic wording or command traces.
- [x] Run `python3 test_build.py`; observe the revised missing-plugin case fail because the old publisher exits 1.
- [x] Update `build.sh`: retain fail-fast and tracing, push the image first, then use `docker help pushrm` to choose between warning and skipping or uploading README. Preserve the build command, target values, and actual upload error handling.
- [x] Run `sh -n build.sh`, `python3 test_build.py`, and `python3 test_split.py`; expect successful exit and regression success messages.
- [x] Smoke the actual publishing script with an isolated Docker stand-in: missing plugin plus successful build warns and exits zero; missing plugin plus failed build still fails. No live image or Hub mutations.
- [x] Update README with optional installation, Docker login/PAT permissions, `./build.sh`, the non-blocking warning, and the standalone README upload retry. Document `python3 test_build.py`.
- [x] Review the small change against the spec and record verification results below; leave product changes uncommitted for the user.

## Execution notes

- Execute inline in the current workspace and preserve unrelated changes. A separate worktree or single-task delegation would add coordination without isolating a meaningful independent slice.
- Authentication permissions remain the plugin's documented prerequisite; do not probe or publish using the user's credentials during verification.
- Revised regression failed on the old missing-plugin exit 1; all six scenarios pass after the correction. `sh -n build.sh` also passed.
- Initial implementation verification ran both `test_build.py` and `test_split.py` in a temporary environment populated from unchanged `requirements.txt`, because system Python lacked `chardet`. This correction changes no Python audio-processing code; the publishing regression was rerun.
- Missing-plugin smoke after the correction observed a warning, successful image-push state, and exit 0. With an injected build failure, it observed no image and exit 17 instead.
- No plugin installation or live publication was performed; temporary smoke files were removed.
- Self-review covered the updated spec and review-focus conditions. No secrets were added, existing image/build settings remain unchanged, and unrelated Python/README work was preserved.
- Excluded the new `test_build.py` from the Docker build context: the existing `ADD *.py .` would otherwise copy the publishing regression into the image. Existing Python files and exclusions are unchanged.
