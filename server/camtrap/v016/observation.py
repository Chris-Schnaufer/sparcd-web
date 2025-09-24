""" Implementation of CamTrap Observation """

class Observation:
    """ Contains Observation data:
    https://github.com/tdwg/camtrap-dp/blob/0.1.6/observations-table-schema.json
    """
    # pylint: disable=too-few-public-methods
    observation_id = ""
    deployment_id = ""
    sequence_id = ""
    media_id = ""
    timestamp = ""
    observation_type = ""
    camera_setup = ""
    taxon_id = ""
    scientific_name = ""
    count = 0
    count_new = 0
    life_stage = ""
    sex = ""
    behaviour = ""
    individual_id = ""
    classification_method = ""
    classified_by = ""
    classification_timestamp = ""
    classification_confidence = 1.0000
    comments = ""

    def __init__(self, observation_id: str):
        """ Instance initialization
        Arguments:
            observation_id: the ID of this observation
        """
        self.observation_id = observation_id
