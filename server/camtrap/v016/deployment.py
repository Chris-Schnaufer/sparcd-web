""" Implementation of CamTrap Deployment """

class Deployment:
    """ Contains Deployment data:
    https://github.com/tdwg/camtrap-dp/blob/0.1.6/deployments-table-schema.json
    """
    # pylint: disable=too-few-public-methods
    deployment_id = ""
    location_id = ""
    location_name = ""
    longitude = 0.0
    latitude = 0.0
    coordinate_uncertainty = 0
    start_timstamp = ""
    end_timestamp = ""
    setup_by = ""
    camera_id = ""
    camera_model = ""
    camera_interval = 0
    camera_height = 0.0
    camera_tilt = 0.0
    camera_heading = 0
    timestamp_issues = False
    bait_use = ""
    session = ""
    array = ""
    feature_type = ""
    habitat = ""
    tags = ""
    comments = ""

    def __init__(self, deployment_id: str):
        """ Initialize class instance
        Arguments:
            deployment_id: the ID of the deployment
        """
        self.deployment_id = deployment_id
