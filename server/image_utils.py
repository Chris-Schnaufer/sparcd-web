""" Utlities for images"""

import subprocess
from typing import Optional
from dateutil import parser

EXIFTOOL_ORIGINAL_DATE = 'DateTimeOriginal'
EXIFTOOL_MODIFY_DATE = 'ModifyDate'
EXIF_CODE_SPARCD = "Exif_0x0227"
EXIF_CODE_SPECIES = "Exif_0x0228"
EXIF_CODE_LOCATION = "Exif_0x0229"


def _parse_exiftool_readout(parse_lines: tuple) -> tuple:
    """ Parses the output from an exiftool binary listing
    Arguments:
        parse_lines: a tuple of the lines to parse
    Return:
        Returns a tuple of the found location, species, and date
    """
    # Disable pylint message about too many branches here
    # pylint: disable=too-many-branches
    skip_line = 0
    found_species = False
    found_location = False
    date_string = ''
    species_string = ''
    location_string = ''
    for one_line in parse_lines:
        if skip_line > 0:
            skip_line = skip_line - 1
            continue
        if EXIFTOOL_ORIGINAL_DATE in one_line:
            skip_line = 0
            # Only use the original date if we don't have a modification date
            if not date_string and '=' in one_line:
                date_string = one_line[one_line.index('=') + 1:].strip()
        elif EXIFTOOL_MODIFY_DATE in one_line:
            skip_line = 0
            if '=' in one_line:
                date_string = one_line[one_line.index('=') + 1:].strip()
        elif EXIF_CODE_SPECIES in one_line:
            skip_line = 1
            found_species = True
            found_location = False
            continue
        elif EXIF_CODE_LOCATION in one_line:
            skip_line = 1
            found_location = True
            found_species = False
            continue
        if found_species is True:
            if '[' in one_line:
                species_string = species_string + one_line[one_line.index('[') + 1:].rstrip(']')
            else:
                found_species = False
        elif found_location is True:
            if '[' in one_line:
                location_string = location_string + one_line[one_line.index('[') + 1:].rstrip(']')
            else:
                found_location = False

    return location_string, species_string, date_string


def _split_species_string(species: str) -> tuple:
    """ Splits the EXIF string into an array of species information
    Arguments:
        species :the EXIT species string
    Returns:
        A tuple of species information strings
    """
    return_species = []
    working_str = species
    last_sep = 0
    cur_start = 0
    while True:
        cur_sep = working_str.find(',', last_sep)
        if cur_sep == -1:
            break
        last_sep = cur_sep + 1
        cur_sep = working_str.find(',', last_sep)
        if cur_sep == -1:
            break
        last_sep = cur_sep + 1
        cur_sep = working_str.find('.', last_sep)
        if cur_sep == -1:
            break
        last_sep = cur_sep + 1
        return_species.append(working_str[cur_start:cur_sep])
        cur_start = last_sep + 0
        if cur_start > len(species):
            break
    return return_species


def get_embedded_image_info(image_path: str) -> Optional[tuple]:
    """ Loads the embedded SPARCd information
    Arguments:
        image_path: the path of the image to check
    Returns:
        Retuns a tuple containing the species and location information that was
        embedded in the image
    """

    try:
        cmd = ["exiftool", "-U", "-v3", image_path]
        res = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as ex:
        print(f'ERROR: Exception getting exif information on image {image_path}', flush=True)
        print(f'       {ex}', flush=True)
        return None, None, None

    location_string, species_string, date_string = \
                                    _parse_exiftool_readout(res.stdout.decode("utf-8").split('\n'))

    if len(species_string) <= 0 and len(location_string) <= 0:
        del res
        print(f"WARNING: no species or locations found in image: {image_path}", flush=True)
        return None, None, None

    return_species = []
    if len(species_string) > 0:
        for one_species in _split_species_string(species_string):
            common, scientific, count = [val.strip() for val in one_species.split(',')]
            return_species.append({'common': common, 'scientific': scientific, 'count': count})

    if len(location_string) > 0:
        locs = location_string.rstrip('.').split('.')
        return_location = {"name": locs[0], "id": locs[len(locs)-1]}
        if len(locs) == 4:
            return_location["elevation"] = locs[1] + '.' + locs[2]
        elif len(locs) == 3:
            return_location["elevation"] = locs[1]
        else:
            print("WARNING: Unknown location format in image, returning 0 for elevation",
                                                                                        flush=True)
            return_location["elevation"] = 0

    del res
    return return_species, return_location, parser.parse(date_string)



def write_embedded_image_info(image_path: str, config_path: str, species_path: str=None, \
                                                                        loc_path: str=None) -> bool:
    """ Updates the embedded SPARCd information
    Arguments:
        image_path: the path of the image to update
        config_path: the path to the exiftool configuration file
        species_path: optional path to the binary data for the species
        loc_path: optional path to the binary data for the location
    Return:
        Returns True if the file was updated and False if a problem ocurred
    """
    # Check for nothing to do
    if not species_path and not loc_path:
        return True

    # Setup the command to execute
    cmd = ["exiftool", "-config", config_path]
    cmd.append("-SanimalFlag=1")
    if species_path:
        cmd.append(f"'-Species<={species_path}'")
    if loc_path:
        cmd.append(f"'-Location<={loc_path}'")
    cmd.append(image_path)

    # Run the command
    try:
        print('HACK: EXIFTOOL UPDATE:', cmd, flush=True)
        res = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as ex:
        print(f'ERROR: Exception setting exif information into image {image_path}', flush=True)
        print(f'       {ex}', flush=True)
        return False

    return True
