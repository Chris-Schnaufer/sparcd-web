/** @module components/Settings */

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import ExitToAppOutlinedIcon from '@mui/icons-material/ExitToAppOutlined';
import Grid from '@mui/material/Grid';
import GlobalStyles from '@mui/material/GlobalStyles';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import PropTypes from 'prop-types';

import { Level } from './Messages';
import { AddMessageContext, CollectionsInfoContext, LocationsInfoContext, SizeContext, SpeciesInfoContext, TokenContext } from '../serverInfo';
import * as utils from '../utils';

/**
 * Returns the UI for administrator tasks
 * @function
 * @param {boolean} loadingCollections Flag indicating collections are being loaded
 * @param {boolean} loadingLocations Flag indicating locations are being loaded
 * @param {boolean} loadingSpecies Flag indicating species are being loaded
 */
export default function SettingsAdmin({loadingCollections, loadingLocations}) {
  const theme = useTheme();
  const addMessage = React.useContext(AddMessageContext); // Function adds messages for display
  const collectionInfo = React.useContext(CollectionsInfoContext);
  const locationItems = React.useContext(LocationsInfoContext);
  const settingsToken = React.useContext(TokenContext);  // Login token
  const uiSizes = React.useContext(SizeContext);  // UI Dimensions
  const panelsWrapperRef = React.useRef(null);  // Used for sizeing
  const [activeTab, setActiveTab] = React.useState(0);
  const [detailsHeight, setDetailsHeight] = React.useState(500); // Height for displaying details
  const [masterSpecies, setMasterSpecies] = React.useState(null); // Contains information on species
  const [serverURL, setServerURL] = React.useState(utils.getServer());  // The server URL to use
  const [userInfo, setUserInfo] = React.useState(null); // Contains information on users

  const [selectedCollections, setSelectedCollections] = React.useState(loadingCollections ? [] : collectionInfo); // Used for searches
  const [selectedLocations, setSelectedLocations] = React.useState(loadingLocations ? [] : locationItems); // Used for searches
  const [selectedSpecies, setSelectedSpecies] = React.useState(masterSpecies || []); // Used for searches
  const [selectedUsers, setSelectedUsers] = React.useState(userInfo || []); // Used for searches

  // Recalcuate available space in the window
  React.useLayoutEffect(() => {
    if (panelsWrapperRef && panelsWrapperRef.current) {
      let footerHeight = 40;
      let headingsHeight = 77;

      let el = document.getElementById('admin-settings-footer');
      if (el) {
        const elRect = el.getBoundingClientRect();
        footerHeight = elRect.height;
      }

      el = document.getElementById('admin-settings-details');
      let el2 = document.getElementById('admin-settings-panel-wrapepr');
      if (el && el2) {
        let elRect = el.getBoundingClientRect();
        let elRect2 = el2.getBoundingClientRect();
        headingsHeight = elRect.top - elRect2.top;
      }

      setDetailsHeight(panelsWrapperRef.current.offsetHeight - footerHeight - headingsHeight);
    }
  }, [activeTab,panelsWrapperRef,setDetailsHeight]);

  /**
   * Updates fields when a new tab is selected for display
   * @function
   * @param {object} event The triggering event object
   * @param {object} newValue The new tab value
   */
  function handleTabChange(event, newValue) {
    setActiveTab(newValue);
  }

  /**
   * Internal TabPanel element type
   * @function
   * @param {object} props The properties of the TabPanel element
   * @returns {object} Returns the UI for the TabPanel
   */
  function TabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`query-results-tabpanel-${index}`}
        aria-labelledby={`query-results-${index}`}
        {...other}
      >
      {value === index && (
        <Box id='tabpanel-box'>
          {children}
        </Box>
      )}
      </div>
    );
  }

  // Define the types of the properties accepted by the TabPanel
  TabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
  };

  /**
   * Returns the a11y properties for a tab control
   * @function
   * @param {integer} index The index of the tab
   * @returns {object} The properties to use for the tab
   */
  function a11yPropsTabPanel(index) {
    return {
      id: `admin-settings-${index}`,
      'aria-controls': `admin-settings-${index}`,
    };
  }

  /**
   * Gets the user information from the server
   * @function
   */
  function getUserInfo() {
    const settingsCheckUrl = serverURL + '/adminUsers?t=' + encodeURIComponent(settingsToken);
    console.log('HACK:ADMINUSERS');

    try {
      const resp = fetch(settingsCheckUrl, {
        method: 'GET',
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed to get admin users: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
            // Set the user data
            console.log('HACK:ADMINUSERS:',respData);
            setUserInfo(respData);
            setSelectedUsers(respData);
        })
        .catch(function(err) {
          console.log('Admin Users Error: ',err);
          addMessage(Level.Warning, 'An error ocurred when attempting to load user information');
      });
    } catch (error) {
      console.log('Admin Users Unknown Error: ',err);
      addMessage(Level.Warning, 'An unknwn error ocurred when attempting to load user information');
    }    
  }

  /**
   * Gets the master species information from the server (not the per-user species)
   * @function
   */
  function getMasterSpecies() {
    const settingsCheckUrl = serverURL + '/adminSpecies?t=' + encodeURIComponent(settingsToken);
    console.log('HACK:ADMINSPECIES');

    try {
      const resp = fetch(settingsCheckUrl, {
        method: 'GET',
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed to get admin species: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
            // Set the species data
            console.log('HACK:ADMINSPECIES:',respData);
            setMasterSpecies(respData);
            setSelectedSpecies(respData);
        })
        .catch(function(err) {
          console.log('Admin Species Error: ',err);
          addMessage(Level.Warning, 'An error ocurred when attempting to load species information');
      });
    } catch (error) {
      console.log('Admin Species Unknown Error: ',err);
      addMessage(Level.Warning, 'An unknwn error ocurred when attempting to load species information');
    }
  }

  /**
   * Handles the new user button press
   * @function
   * @param {object} event The triggering event
   * @param {object} {location} The user object to edit or falsy if a new user is wanted
   */
  function handleUserEdit(event, user) {
    console.log('HACK:HANDLEUSER',user);
    event.stopPropagation();
  }

  /**
   * Handles the new collection button press
   * @function
   * @param {object} event The triggering event
   * @param {object} {location} The collection object to edit or falsy if a new collection is wanted
   */
  function handleCollectionEdit(event, collection) {
    console.log('HACK:HANDLECOLLECTION',collection);
    event.stopPropagation();
  }

  /**
   * Handles the new species button press
   * @function
   * @param {object} event The triggering event
   * @param {object} {location} The species object to edit or falsy if a new species is wanted
   */
  function handleSpeciesEdit(event, species) {
    console.log('HACK:HANDLESPECIES',species);
    event.stopPropagation();
  }

  /**
   * Handles the new location button press
   * @function
   * @param {object} event The triggering event
   * @param {object} {location} The location object to edit or falsy if a new location is wanted
   */
  function handleLocationEdit(event, location) {
    console.log('HACK:HANDLELOCATION',location);
    event.stopPropagation();
  }

  /**
   * Handles the user search button press
   * @function
   * @param {object} event The change event for searching
   */
  function searchUsers(event) {
    if (event.target.value && userInfo) {
      const ucSearch = event.target.value.toUpperCase();
      setSelectedUsers(userInfo.filter((item) => item.name.toUpperCase().includes(ucSearch) || item.email.toUpperCase().includes(ucSearch) ));
    } else {
      setSelectedUsers(userInfo || []);
    }
  }

  /**
   * Handles the collection search button press
   * @function
   * @param {object} event The change event for searching
   */
  function searchCollections(event) {
    if (event.target.value && !loadingCollections) {
      const ucSearch = event.target.value.toUpperCase();
      setSelectedCollections(collectionInfo.filter((item) => item.name.toUpperCase().includes(ucSearch) || item.id.toUpperCase().includes(ucSearch) ||
                                                                    item.email.toUpperCase().includes(ucSearch) ));
    } else {
      setSelectedCollections(loadingCollections ? [] : collectionInfo);
    }
  }

  /**
   * Handles the species search button press
   * @function
   * @param {object} event The change event for searching
   */
  function searchSpecies(event) {
    if (event.target.value && masterSpecies) {
      const ucSearch = event.target.value.toUpperCase();
      setSelectedSpecies(masterSpecies.filter((item) => item.name.toUpperCase().includes(ucSearch) || item.scientificName.toUpperCase().includes(ucSearch) ));
    } else {
      setSelectedSpecies(masterSpecies || []);
    }
  }

  /**
   * Handles the location search button press
   * @function
   * @param {object} event The change event for searching
   */
  function searchLocations(event) {
    if (event.target.value && !loadingLocations) {
      const ucSearch = event.target.value.toUpperCase();
      setSelectedLocations(locationItems.filter((item) => item.nameProperty.toUpperCase().includes(ucSearch) || item.idProperty.toUpperCase().includes(ucSearch) ));
    } else {
      setSelectedLocations(loadingLocations ? [] : locationItems);
    }
  }

  /**
   * Returns the UI for editing users. Starts the user information fetch if we don't have it already
   * @function
   * @param {function} dblClickFunc Function to handle the user double clicking on a row
   */
  function generateUsers(dblClickFunc) {
    let curUserInfo = selectedUsers || [];
    if (userInfo == null) {
      getUserInfo();
      setUserInfo([]);
      setSelectedUsers([]);
    }
    if (curUserInfo.length <= 0) {
      return (
        <Grid container justifyContent="center" alignItems="center" sx={{position:'absolute',top:'0px', right:'0px', bottom:'0px', left:'0px'}} >
          <CircularProgress />
        </Grid>
      );
    }

    dblClickFunc = dblClickFunc ? dblClickFunc : () => {};
    return (
      <table id='admin-settings-users-details-wrapper' style={{width:'100%', padding:'0px 5px 0 5px', borderCollapse:"collapse"}} >
        <thead id="admin-settings-collection-header" style={{width:'100%', backgroundColor:'lightgrey'}} >
        <tr>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold', paddingLeft:'5px'}}>
              Name
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold'}}>
              Email
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold'}}>
              Collections
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold'}}>
              Admin
            </Typography>
          </th>
          <th scope="col" style={{leftMargin:'auto', borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold', paddingRight:'5px'}}>
              Auto
            </Typography>
          </th>
        </tr>
        </thead>
        <tbody id='admin-settings-details' style={{overflowY:'scroll', width:'100%', maxHeight:detailsHeight+'px', display:'block' }}>
        <GlobalStyles styles={{ tr: { width:'100%', '&:hover':{backgroundColor:'rgba(0,0,0,0.05)'} } }} />
        { curUserInfo.map((item,idx) => 
            <tr key={item.name+'-'+idx} onDoubleClick={(event) => dblClickFunc(event,item)} >
              <td style={{padding:'0px 5px 0px 5px'}}>
                <Typography nowrap="true" variant="body2">
                  {item.name}
                </Typography>
              </td>
              <td style={{padding:'0px 5px 0px 5px'}}>
                <Typography nowrap="true" variant="body2">
                  {item.email}
                </Typography>
              </td>
              <td style={{padding:'0px 5px 0px 5px'}}>
                <Typography nowrap="true" variant="body2">
                  { item.collections.map((colItem, colIdx) => 
                      <React.Fragment key={colItem.name+'-'+colIdx}>
                        {colIdx > 0 && ', '}
                        {colItem.name}
                        <span style={{fontWeight:'bold', fontSize:'small'}}>
                          &nbsp;(
                          {colItem.owner && 'O'}
                          {colItem.read && 'R'}
                          {colItem.write && 'W'}
                          )
                        </span>
                      </React.Fragment>
                  )}
                </Typography>
              </td>
              <td style={{padding:'0px 5px 0px 5px'}}>
                <Typography nowrap="true" variant="body2" align="center">
                  {item.admin ? 'Y' : ' '}
                </Typography>
              </td>
              <td style={{padding:'0px 5px 0px 5px'}}>
                <Typography nowrap="true" variant="body2" align="center">
                  {item.auto ? 'Y' : 'N'}
                </Typography>
              </td>
            </tr>
        )}
        </tbody>
      </table>
    );
  }

  /**
   * Returns the UI for editing Collections
   * @function
   * @param {function} dblClickFunc Function to handle the user double clicking on a row
   */
  function generateCollections(dblClickFunc) {
    if (loadingCollections) {
      return (
        <Grid container justifyContent="center" alignItems="center" sx={{position:'absolute',top:'0px', right:'0px', bottom:'0px', left:'0px'}} >
          <CircularProgress />
        </Grid>
      );
    }

    dblClickFunc = dblClickFunc ? dblClickFunc : () => {};
    return (
      <table id='admin-settings-collections-details-wrapper' style={{width:'100%', padding:'0px 5px 0 5px', borderCollapse:"collapse"}} >
        <thead id="admin-settings-collection-header" style={{width:'100%', backgroundColor:'lightgrey'}} >
        <tr>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold', paddingLeft:'5px'}}>
              Name
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold'}}>
              ID
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px', marginLeft:'auto'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold', paddingRight:'5px'}}>
              email
            </Typography>
          </th>
        </tr>
        </thead>
        <tbody id='admin-settings-details' style={{overflowY:'scroll',width:'100%', maxHeight:detailsHeight+'px', display:'block' }}>
        <GlobalStyles styles={{ tr: { width:'100%', '&:hover':{backgroundColor:'rgba(0,0,0,0.05)'} } }} />
        { selectedCollections.map((item, idx) => 
            <tr id={"admin-species-"+idx} key={item.name+'-'+idx} onDoubleClick={(event) => dblClickFunc(event,item)} >
              <td style={{padding:'0px 5px 0px 5px'}}>
                <Typography nowrap="true" variant="body2">
                  {item.name}
                </Typography>
              </td>
              <td style={{padding:'0px 5px 0px 5px'}}>
                <Typography nowrap="true" variant="body2">
                  {item.id}
                </Typography>
              </td>
              <td style={{padding:'0px 5px 0px 5px', leftMargin:'auto'}}>
                <Typography nowrap="true" variant="body2">
                  {item.email}
                </Typography>
              </td>
            </tr>
        )}
        </tbody>
      </table>
    );
  }

  /**
   * Returns the UI for editing the main species list. Starts the main species fetch if we don't have it already
   * @function
   * @param {function} dblClickFunc Function to handle the user double clicking on a row
   */
  function generateSpecies(dblClickFunc) {
    let curSpecies = selectedSpecies || [];
    if (masterSpecies == null) {
      getMasterSpecies();
      setMasterSpecies([]);
      setSelectedSpecies([]);
    }
    if (curSpecies.length <= 0) {
      return (
        <Grid container justifyContent="center" alignItems="center" sx={{position:'absolute',top:'0px', right:'0px', bottom:'0px', left:'0px'}} >
          <CircularProgress />
        </Grid>
      );
    }

    dblClickFunc = dblClickFunc ? dblClickFunc : () => {};
    return (
      <table id='admin-settings-species-details-wrapper' style={{width:'100%', padding:'0px 5px 0 5px', borderCollapse:"collapse"}} >
        <thead id="admin-settings-species-header" style={{width:'100%', backgroundColor:'lightgrey'}} >
        <tr>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold', paddingLeft:'5px'}}>
              Name
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold'}}>
              Scientific Name
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px', marginLeft:'auto'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold', paddingRight:'5px'}}>
              Key Binding
            </Typography>
          </th>
        </tr>
        </thead>
        <tbody id='admin-settings-details' style={{overflowY:'scroll',width:'100%', maxHeight:detailsHeight+'px', display:'block' }}>
        <GlobalStyles styles={{ tr: { width:'100%', '&:hover':{backgroundColor:'rgba(0,0,0,0.05)'} } }} />
        { curSpecies.map((item, idx) => 
              <tr id={"admin-species-"+idx} key={item.name+'-'+idx} onDoubleClick={(event) => dblClickFunc(event,item)} >
                <td style={{padding:'0px 5px 0px 5px'}}>
                  <Typography nowrap="true" variant="body2">
                    {item.name}
                  </Typography>
                </td>
                <td style={{padding:'0px 5px 0px 5px'}}>
                  <Typography nowrap="true" variant="body2">
                    {item.scientificName}
                  </Typography>
                </td>
                <td style={{padding:'0px 5px 0px 5px', leftMargin:'auto'}}>
                  <Typography nowrap="true" variant="body2" align="center">
                    {item.keyBinding}
                  </Typography>
                </td>
              </tr>
        )}
        </tbody>
      </table>
    );
  }

  /**
   * Returns the UI for editing Locations
   * @function
   * @param {function} dblClickFunc Function to handle the user double clicking on a row
   */
  function generateLocations(dblClickFunc) {
    if (loadingLocations) {
      return (
        <Grid container justifyContent="center" alignItems="center" sx={{position:'absolute',top:'0px', right:'0px', bottom:'0px', left:'0px'}} >
          <CircularProgress />
        </Grid>
      );
    }

    dblClickFunc = dblClickFunc ? dblClickFunc : () => {};
    return (
      <table id='admin-settings-locations-details-wrapper' style={{width:'100%', padding:'0px 5px 0 5px', borderCollapse:"collapse"}} >
        <thead id="admin-settings-species-header" style={{width:'100%', backgroundColor:'lightgrey'}} >
        <tr>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold', paddingLeft:'5px'}}>
              Name
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold'}}>
              ID
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold'}} align="center" >
              Active
            </Typography>
          </th>
          <th scope="col" style={{borderBottom:'1px solid grey', padding:'0px 10px 0px 10px', marginLeft:'auto'}}>
            <Typography nowrap="true" variant="body" style={{fontWeight:'bold', paddingRight:'5px'}}>
              Location
            </Typography>
          </th>
        </tr>
        </thead>
        <tbody id='admin-settings-details' style={{overflowY:'scroll', width:'100%', maxHeight:detailsHeight+'px', display:'block' }}>
        <GlobalStyles styles={{ tr: { width:'100%', '&:hover':{backgroundColor:'rgba(0,0,0,0.05)'} } }} />
        { selectedLocations.map((item, idx) => {
            const extraAttribs = item.activeProperty || idx == 0 ? {} : {color:'grey'};
            return (
              <tr id={"admin-species-"+idx} key={item.name+'-'+idx} style={{...extraAttribs}} onDoubleClick={(event) => dblClickFunc(event,item)} >
                <td style={{padding:'0px 5px 0px 5px'}}>
                  <Typography nowrap="true" variant="body2" >
                    {item.nameProperty}
                  </Typography>
                </td>
                <td style={{padding:'0px 5px 0px 5px'}}>
                  <Typography nowrap="true" variant="body2">
                    {item.idProperty}
                  </Typography>
                </td>
                <td style={{padding:'0px 5px 0px 5px'}}>
                  <Typography nowrap="true" variant="body2" align="center">
                    {item.activeProperty || idx == 0 ? 'Y' : ' '}
                  </Typography>
                </td>
                <td style={{padding:'0px 5px 0px 5px'}}>
                  <Typography nowrap="true" variant="body2" align="right" style={{whiteSpace:'pre'}}>
                    {item.latProperty + ', ' + item.lngProperty}
                  </Typography>
                </td>
              </tr>
            );}
        )}
        </tbody>
      </table>
    );
  }

  // Setup the tab and page generation
  const adminTabs = [
    {name:'Users', uiFunc:() => generateUsers(handleUserEdit), newName:'Add User', newFunc:handleUserEdit, searchFunc:searchUsers},
    {name:'Collections', uiFunc:() => generateCollections(handleCollectionEdit), newName:'Add Collection', newFunc:handleCollectionEdit, searchFunc:searchCollections},
    {name:'Species', uiFunc:() => generateSpecies(handleSpeciesEdit), newName:'Add Species', newFunc:handleSpeciesEdit, searchFunc:searchSpecies},
    {name:'Locations', uiFunc:() => generateLocations(handleLocationEdit), newName:'Add Location', newFunc:handleLocationEdit, searchFunc:searchLocations},
  ];

  const activeTabInfo = adminTabs[activeTab];
  return (
      <Grid id="settings-admin-wrapper" container direction="row" alignItems="center" justifyContent="center"
            sx={{position:'absolute', top:0, left:0, width:'100vw', height:'100vh', backgroundColor:'rgb(0,0,0,0.5)', zIndex:55555}}
      >
      <Grid container size="grow" alignItems="start" justifyContent="start" sx={{padding:'15px 15px', borderRadius:'20px', overflow:'scroll'}}>
        <Grid size={1}  sx={{backgroundColor:"#EAEAEA", borderRadius:'10px 0px 0px 10px'}}>
          <Tabs id='settings-admin-tabs' value={activeTab} onChange={handleTabChange} aria-label="Administrator Settings Edit" orientation="vertical" variant="scrollable"
                scrollButtons={false} style={{overflow:'scroll', maxHeight:'100%'}}>
            { adminTabs.map((item, idx) =>
                <Tab id={'admin-settings-tab-'+idx} key={item.name+'-'+idx} label={
                            <Typography gutterBottom variant="body2" sx={{'&:hover':{fontWeight:'bold'} }}>
                              {item.name}
                            </Typography>
                         }
                   key={idx} {...a11yPropsTabPanel(idx)} sx={{'&:hover':{backgroundColor:'rgba(0,0,0,0.05)'} }}
                />
              )
            }
            <Tab sx={{paddingTop:'20px'}} label={
                      <Grid container direction="row" justifyContent="start" alignItems="center" sx={{width:'100%', '&:hover':{borderBottom:'1px solid black'} }}>
                        <Grid size={'grow'} justifyContent="start">
                        <Typography gutterBottom variant="body2" sx={{'&:hover':{fontWeight:'bold'} }}>
                          Done
                        </Typography>
                        </Grid>
                        <div style={{marginLeft:'auto'}} >
                          <ExitToAppOutlinedIcon />
                        </div>
                      </Grid>
                     }
               key={adminTabs.length} {...a11yPropsTabPanel(99)} sx={{'&:hover':{backgroundColor:'rgba(0,0,0,0.05)'} }}
            />
          </Tabs>
        </Grid>
        <Grid id='admin-settings-panel-wrapepr' ref={panelsWrapperRef} size={11} sx={{backgroundColor:'#EAEAEA', borderRadius:'0px 25px 25px 25px'}}>
          { adminTabs.map((item,idx) => 
              <TabPanel id={'admin-settings-panel-'+item.name} key={item.name+'-'+idx}  value={activeTab} index={idx}
                        style={{width:'100%', position:'relative', height:uiSizes.workspace.height+'px'}}>
                <Grid id="admin-settings-panel-wrapper" container direction="column" justifyContent="center" alignItems="center" sx={{width:'100%'}} >
                  <Typography gutterBottom variant="h4" component="h4">
                    Administration - {item.name}
                  </Typography>
                  {item.uiFunc()}
                </Grid>
              </TabPanel>
            )
          }
          <TabPanel id={'admin-settings-panel-done'} value={activeTab} index={adminTabs.length} key={'done-'+adminTabs.length} 
                    style={{width:'100%', position:'relative',margin:'0 16px auto 8px', height:uiSizes.workspace.height+'px'}}>
            COMPLETED
          </TabPanel>
          <Grid id='admin-settings-footer' container direction="row" justifyContent="space-between" alignItems="center" 
                sx={{position:'sticky',bottom:'0px',backgroundColor:'#F0F0F0', borderTop:'1px solid black', boxShadow:'lightgrey 0px -3px 3px',
                     padding:'5px 20px 5px 20px', width:'100%'}}>
            <Grid>
              <Button id="admin-settings-add-new" size="small" onClick={activeTabInfo.newFunc}>{activeTabInfo.newName}</Button>
            </Grid>
            <Grid>
              <TextField id="search" label={'Search'} placehoder={'Search'} size="small" variant="outlined"
                        onChange={activeTabInfo.searchFunc}
                        slotProps={{
                          input: {
                            endAdornment:
                              <InputAdornment position="end">
                                <IconButton
                                  aria-label="Searching"
                                  onClick={activeTabInfo.searchFunc}
                                >
                                  <SearchOutlinedIcon />
                                </IconButton>
                              </InputAdornment>
                          },
                        }}
             />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      </Grid>
  );
}
