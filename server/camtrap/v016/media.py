""" Implementation of CamTrap Media """

class Media:
    """ Contains Media data:
    https://github.com/tdwg/camtrap-dp/blob/0.1.6/media-table-schema.json
    """
    # pylint: disable=too-few-public-methods
    media_id = ""
    deployment_id = ""
    sequence_id = ""
    capture_method = ""
    timestamp = ""
    file_path = ""
    file_name = ""
    file_media_type = ""
    exif_data = ""
    favorite = False
    comments = ""

    def __init__(self, media_id: str):
        """ Instance initialization
        Arguments:
            media_id: the ID of the media
        """
        self.media_id = media_id
