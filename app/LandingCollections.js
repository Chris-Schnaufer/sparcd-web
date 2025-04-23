'use client'

/** @module LandingCollections */

import * as React from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import { BaseURLContext, CollectionsInfoContext, MobileDeviceContext, TokenContext } from './serverInfo'

/** Returns the UI of the collections for the Landing page
 * @function
 * @param {function} onCollectionInfo The function to receive the list of collection information
 * @param {function} onChange Function for when a collection selection has changed
 * @returns {object} The rendered UI
 */
export default function LandingCollections({onCollectionInfo, onChange}) {
  const theme = useTheme();
  const curCollectionsInfo = React.useContext(CollectionsInfoContext);
  const collectionToken = React.useContext(TokenContext);
  const baseUrl = React.useContext(BaseURLContext);
  const mobileDevice = React.useContext(MobileDeviceContext);  // TODO: Are we on a mobile device (portrait mode)
  const [collectionsList, setCollectionsList] = React.useState(null);
  const [refreshingUploads, setRefreshingUploads] = React.useState(false);
  const [selectedCollection, setSelectedCollection] = React.useState(null);

  /**
   * Fetches the collections from the server
   * @function
   */
  function getCollections() {
/*    const collectionUrl =  baseUrl + '/collections&' + collectionToken
    try {
      setRefreshingUploads(true);
      const resp = fetch(collectionUrl, {
        credentials: 'include',
        method: 'GET'
      }).then(async (resp) => {
              if (resp.ok) {
                return resp.json();
              } else {
                throw new Error(`Failed to get collections: ${resp.status}`, {cause:resp});
              }
          })
        .then((respData) => {
            // Save response data
            setRefreshingUploads(false);
        })
        .catch(function(err) {
          console.log('Error: ',err);
          if (onFailure && typeof(onFailure) === 'function') {
            onFailure();
          }
      });
    } catch (error) {
      if (onFailure && typeof(onFailure) === 'function') {
        onFailure();
      }
    }
*/
    return [{'name': 'foo',
             'organization': '! lovely collection',
             'email': 'foo@google.com',
             'description': '88888888-4444-4444-4444-121212121212',
             'bucket': '88888888-4444-4444-4444-121212121212',
             'id': '11111111-4444-4444-4444-121212121212',
             'uploads': []
            }, 
            {'name': 'bar',
             'organization': 'My lovely collection',
             'email': 'bar@google.com',
             'description': '88888888-4444-4444-4444-121212121212',
             'bucket': '88888888-4444-4444-4444-121212121212',
             'id': '22222222-4444-4444-4444-121212121212',
             'uploads': [
              {
                'name': 'schnaufer on 2024-07-16 at 11:56',
                'description': 'Whetstones - WHE12 - 4812 - Uploaded 03-09-2025 - Collected 03-08-2025',
                'imagesCount': 100,
                'imagesWithSpeciesCount': 100,
                'location':'CAN06', 
                'edits': [{'name':'smalusa','date':'2024.10.26.09.18.19'},
                         {'name':'smalusa','date':'2024.10.27.13.36.03'},
                        ]
              }, {
                'name':'schnaufer on 2024-90-11 at 10:22',
                'description': 'Whetstones - WHE12 - 800 - uploaded 09-12-2024 - collected 09-11-2024',
                'imagesCount': 130,
                'imagesWithSpeciesCount': 120,
                'location':'CAN06', 
                'edits': [{'name':'lizt','date':'2024.09.19.16.07.17'},
                        ]
              }, {
                'name':'schnaufer on 2024-10-13 at 13:04',
                'description': 'Whetstones - WHE12 - 2100 - uploaded 10-13-2024 - collected 10-12-2024',
                'imagesCount': 4000,
                'imagesWithSpeciesCount': 3998,
                'location':'CAN06', 
                'edits': [{'name':'lizt','date':'2024.05.19.15.35.07'},
                        ]
              }
             ]
            },
            {'name': 'zar',
             'organization': '! lovely collection',
             'email': 'zar@google.com',
             'description': '88888888-4444-4444-4444-121212121212',
             'bucket': '88888888-4444-4444-4444-121212121212',
             'id': '33333333-4444-4444-4444-121212121212',
             'uploads': []
            },
            {'name': 'har',
             'organization': '! lovely collection',
             'email': 'har@google.com',
             'description': '88888888-4444-4444-4444-121212121212',
             'bucket': '88888888-4444-4444-4444-121212121212',
             'id': '44444444-4444-4444-4444-121212121212',
             'uploads': []
            },
            {'name': 'gar',
             'organization': '! lovely collection',
             'email': 'gar@google.com',
             'description': '88888888-4444-4444-4444-121212121212',
             'bucket': '88888888-4444-4444-4444-121212121212',
             'id': '55555555-4444-4444-4444-121212121212',
             'uploads': []
            },
            {'name': 'far',
             'organization': '! lovely collection',
             'email': 'far@google.com',
             'description': '88888888-4444-4444-4444-121212121212',
             'bucket': '88888888-4444-4444-4444-121212121212',
             'id': '66666666-4444-4444-4444-121212121212',
             'uploads': []
            },
            {'name': 'dar',
             'organization': '! lovely collection',
             'email': 'dar@google.com',
             'description': '88888888-4444-4444-4444-121212121212',
             'bucket': '88888888-4444-4444-4444-121212121212',
             'id': '77777777-4444-4444-4444-121212121212',
             'uploads': []
            },
            {'name': 'car',
             'organization': '! lovely collection',
             'email': 'car@google.com',
             'description': '88888888-4444-4444-4444-121212121212',
             'bucket': '88888888-4444-4444-4444-121212121212',
             'id': '88888888-4444-4444-4444-121212121212',
             'uploads': []
            }];
    //return [];
  }

  /**
   * Handles a change in the user's selection and calls the parent's change function
   * @function
   * @param {object} event The event object
   */
  function handleChange(event) {
    setSelectedCollection(event.target.value);
    onChange(event.target.value);
  }

  // TODO: cache these
  const collectionItems = curCollectionsInfo;// || getCollections();
  const firstItem = collectionItems && collectionItems.length > 0 ? collectionItems[0] : null;

  // Set the upload info for the parent
/*  React.useEffect(() => {
      function setCollectionInfo() {onCollectionInfo(collectionItems);};
      setCollectionInfo();
    },[]);
*/

  // Render the UI
  return (
    <React.Fragment>
      { firstItem ? (
        <React.Fragment>
          <Typography gutterBottom sx={{ ...theme.palette.landing_collections_refresh,
                      visibility:collectionItems?"visible":"hidden" }} >
            Refreshing...
          </Typography>
          <Box sx={{ ...theme.palette.landing_collections }} >
            <FormControl>
              <RadioGroup
                name='collection-items'
                value={selectedCollection}
                onChange={handleChange}              
              >
                  {
                    collectionItems.map(function(obj, idx) {
                      return <FormControlLabel value={obj.name} control={<Radio />} label={obj.name} key={obj.name} />
                    })
                  }
              </RadioGroup>
            </FormControl>
          </Box>
        </React.Fragment>
        ) : mobileDevice ? <Box>Nothing to do</Box>
            : <Typography gutterBottom sx={{ color: 'text.secondary', fontSize: 14, textAlign: 'center',  }} >
                No collections are available
              </Typography>
      }
    </React.Fragment>
  );
}
