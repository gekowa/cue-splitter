# CLAUDE.md - CUE Splitter Project Guide

## Build and Run Commands
- Run script: `python split.py <directory>`
- Run with Docker: `docker run -v "$(pwd)":/workdir -e PUID=$(id -u) -e PGID=$(id -g) -it --rm gekowa/cue-splitter`
- Build Docker image: `./build.sh`

## Code Style Guidelines
- **Imports**: Group standard library imports first, then third-party modules (chardet, mutagen)
- **Formatting**: Use 4-space indentation
- **Naming**: Use snake_case for variables/functions, CamelCase for classes
- **Error Handling**: Use try/except blocks with specific exception types, log errors with logging module
- **Logging**: Use logging module with proper levels (INFO/WARNING/ERROR)
- **Comments**: Document complex logic with descriptive comments
- **Constants**: Define at the top of the file in UPPERCASE

## Project Structure
- `split.py`: Main Python script for CUE file processing
- `split2flac`: Shell script for splitting audio files
- `Dockerfile`: Container definition with dependencies
- Dependencies: split2flac, Python 3, chardet, mutagen

## Testing
No formal test framework. Test by running with sample CUE files.