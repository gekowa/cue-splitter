"""
Generates MusicBrainz DiscID from track information.
"""
from typing import List, Tuple
import sys
import hashlib
import base64
import os
from os import PathLike
import logging
from pathlib import Path

from mutagen.flac import FLAC


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_discid(track_info: List[Tuple[int, int]]) -> str:
    """
    Generate the MusicBrainz DiscID from track information.
    
    Args:
        track_info: List of tuples containing (track_offset, track_length_in_sectors)
        
    Returns:
        MusicBrainz DiscID as a string
    """

    # First byte is the number of tracks
    num_tracks = len(track_info)

    # Calculate the lead-out position (end of last track)
    last_track_offset, last_track_length = track_info[-1]
    lead_out_offset = last_track_offset + last_track_length

    hex_string = ""

    # Create the data for hashing
    # First byte: First track (usually 1)
    # Second byte: Last track (number of tracks)
    # Next 4 bytes: Lead-out position

    hex_string += f'{1:02X}'
    hex_string += f'{num_tracks:02X}'
    hex_string += f'{lead_out_offset:08X}'

    # Add each track offset (99 tracks max, padded with zeros)
    for i in range(99):
        if i < len(track_info):
            offset, _ = track_info[i]
            hex_string += f'{offset:08X}'
        else:
            hex_string += '00000000'

    # Calculate SHA-1 hash
    sha1 = hashlib.sha1(hex_string.encode('ascii')).digest()
    base64_bytes = base64.b64encode(sha1)

    return base64_bytes.decode('ascii') \
        .replace('+', '.') \
        .replace('/', '_') \
        .replace('=', '-')


def get_flac_duration_with_mutagen(flac_file):
    audio = FLAC(flac_file)
    return audio.info.length


def get_track_offsets_and_lengths(flac_files: List[str]) -> List[Tuple[int, int]]:
    """
    Extract track lengths from FLAC files and calculate offsets.
    
    Args:
        flac_files: List of paths to FLAC files
        
    Returns:
        List of tuples containing (track_offset, track_length_in_sectors)
    """
    track_info = []
    current_offset = 150  # Initial offset is 150 sectors (2 seconds)

    for flac_file in flac_files:
        duration_seconds = get_flac_duration_with_mutagen(flac_file)
        logging.info(f"Duration of {os.path.basename(flac_file)}:\t {round(duration_seconds, 2)} seconds")
        # print(duration_seconds)
        # Convert duration to sectors (75 sectors per second)
        length_sectors = round(duration_seconds * 75)
        
        track_info.append((current_offset, length_sectors))
        current_offset += length_sectors

    # print(track_info)
    return track_info


def generate_discid_of_flacs(flac_folder: PathLike) -> str:
    """
    Calculate MusicBrainz DiscID from a folder of FLAC files.
    
    Args:
        flac_folder: Path to the folder containing FLAC files
        
    Returns:
        MusicBrainz DiscID as a string
    """
    # Get all FLAC files in the folder
    flac_files = [
        os.path.join(flac_folder, f) for f in sorted(os.listdir(flac_folder))
        if f.lower().endswith('.flac')
    ]

    if not flac_files:
        raise ValueError(f"No FLAC files found in {flac_folder}")

    logging.info(f"Found {len(flac_files)} FLAC files.")

    # Get track lengths and offsets
    track_info = get_track_offsets_and_lengths(flac_files)

    # Calculate the DiscID
    return generate_discid(track_info)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        # use current workdir for base_dir
        base_dir = Path.cwd()

        # print("Usage: python pydiscid.py <directory>")
        # sys.exit(1)
    else:
        base_dir = Path(sys.argv[1]).resolve()
        
    logging.info(f"Calculating Disc ID of directory {base_dir}")

    try:
        print("Disc ID: ", generate_discid_of_flacs(base_dir))
    except ValueError as e:
        logging.error(e)
        sys.exit(1)
