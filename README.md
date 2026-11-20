# cue-splitter
A python script splits massive cue+flac tracks. Splitted tracks are saved in the same directory as raw cue&flac and original audio file is removed after double check.


The script transcode every splitted track to CD quality flac because shnsplit, which hasn't updated for over 15 years, do not support splitting higher quality tracks with one-second accuracy cues, while almost no cue file uses milisecond accuracy.

## The script automatically handles: 

- determining which folder needs processing

- codecs of cue files and convert to utf-8 by default

- check & remove original track

- tag muiti-disc albums

## Usage (Python)

```sh
python3 split.py /path/to/music
python3 split.py --skip-filename-check /path/to/music
python3 split.py --help
```

The directory argument is required and is scanned recursively. `-h` / `--help` explains the arguments and exits without processing files.

Filename checks are enabled by default. `--skip-filename-check` bypasses them both when selecting directories to process and when deleting oversized audio after splitting. Audio-extension checks and the existing size-based deletion conditions still apply; the flag can make additional files eligible for deletion.

Run the standalone regression check with `python3 test_split.py` after installing the Python dependencies. It uses temporary files and substitutes external audio commands.

## Usage (Docker)
```
alias cue-splitter='docker run -v "$(pwd)":/workdir -e PUID=$(id -u) -e PGID=$(id -g) -it --rm gekowa/cue-splitter cue-splitter .'
```
Then, 
```
cd music-dir
cue-splitter
cue-splitter --skip-filename-check
cue-splitter --help
```

Arguments after the image name replace Docker's default command. The alias explicitly runs the container's `cue-splitter` wrapper with `.` (the mounted `/workdir`), so additional options reach `split.py`. Without the alias, use `docker run --rm gekowa/cue-splitter cue-splitter --help`; when processing music, also mount its directory at `/workdir` and pass `.`.

The new options require an image containing the updated `split.py`; rebuild the image before using them with an older image.

## Publishing to Docker Hub

To enable automatic overview uploads, install the optional [docker-pushrm CLI plugin](https://github.com/christian-korneck/docker-pushrm#installation). It reuses your Docker login; the account must be allowed to update `gekowa/cue-splitter`. When using a personal access token, the plugin's documentation requires `admin` scope.

From the repository root, with the existing `x86_64` Docker context configured:

```sh
docker login
./build.sh
```

Publishing first pushes `gekowa/cue-splitter:latest`, then uploads `README.md` as its Docker Hub overview if docker-pushrm is installed. If the plugin is missing, the script prints a warning and skips the overview upload; image publishing still succeeds. A failed context/build stops publishing without attempting the overview upload.

If the overview upload fails, the script exits with an error but the image is already published. Fix the reported error, then retry only the overview:

```sh
docker pushrm --file README.md gekowa/cue-splitter
```

Run `python3 test_build.py` to check publishing failure handling without building images or contacting Docker Hub.

## Dependancies

- [split2flac](https://github.com/yuygfgg/split2flac/) and its dependencies (The modified version of split2flac is recommended because it supports album artist and unicode characters.)

- python3

- chardet

- mutagen

## Screenshots
<img width="1320" alt="截屏2024-06-07 14 43 59" src="https://github.com/yuygfgg/cue-splitter/assets/140488233/5664f886-4d03-4f56-8810-e336d7d7ead6">
<img width="1334" alt="截屏2024-06-07 14 45 33" src="https://github.com/yuygfgg/cue-splitter/assets/140488233/108e328a-0059-4bb0-ab45-4f49a18e875b">
<img width="1920" alt="截屏2024-06-08 15 37 18" src="https://github.com/yuygfgg/cue-splitter/assets/140488233/c5495aa1-39f7-4196-87d5-c19c5b179f94">
