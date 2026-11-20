# Automatic Docker Hub overview publishing

## Intent and scope

Every successful image publication through `./build.sh` must upload the repository's `README.md` as the Docker Hub overview for `gekowa/cue-splitter`. Keep README as the sole source; do not rewrite its content or maintain a second overview file.

This is a small publishing-script change. Image contents, build platforms, tags, Docker context, audio processing, and Docker Hub's separate short description remain unchanged. No CI migration, automatic plugin installation, custom HTTP client, or credentials in the repository.

## Approaches

1. **Docker CLI plugin (`docker-pushrm`), selected by the user.** Reuses Docker login and handles the Hub API. Adds a one-time plugin installation, but avoids custom authentication and upload code.
2. **Python standard-library uploader, not selected.** Avoids an additional executable, but requires maintaining API/authentication logic and separate credential handling.

## Publishing behavior

- Continue invoking `./build.sh` from the repository root, as the existing build command requires.
- Check that `docker pushrm` is available before starting the image build. A missing plugin must fail early with installation guidance.
- Stop on a failed context selection or image build/push; never upload an overview for a failed image publication.
- After the existing build-and-push command succeeds, run `docker pushrm --file README.md "${REPO}/${IMAGE}"`. Explicitly select README instead of allowing the plugin to choose another file.
- A failed overview upload must exit nonzero and explain that the image was already pushed. Do not claim rollback or hide the failure. The standalone upload command can retry the overview without rebuilding the image.

These failure-handling and prerequisite choices are assistant proposals, pending approval of this document.

## Setup and documentation

Add a publishing section to README with the upstream plugin installation link, `docker pushrm --help`, Docker login with credentials permitted to update the repository overview, `./build.sh`, and the standalone overview retry command. Existing Docker credential storage remains responsible for secrets; do not pass secrets as command arguments.

## Verification

Check shell syntax and exercise the actual publishing script with a controlled Docker stand-in: successful push followed by upload, missing plugin, failed image publication without upload, and failed overview upload with nonzero status and a partial-success message. Do not publish a real image merely to test this change; report live Hub verification separately if not exercised.

## Builder discretion

Choose the shortest readable shell implementation and diagnostic wording. No new configuration layer or release workflow is needed.

Reference: https://github.com/christian-korneck/docker-pushrm
