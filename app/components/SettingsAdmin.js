/** @module components/Settings */

import * as React from 'react';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import ExitToAppOutlinedIcon from '@mui/icons-material/ExitToAppOutlined';
import Grid from '@mui/material/Grid';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
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
  const [activeTab, setActiveTab] = React.useState(0);
  const [masterSpecies, setMasterSpecies] = React.useState(null); // Contains information on species
  const [serverURL, setServerURL] = React.useState(utils.getServer());  // The server URL to use
  const [userInfo, setUserInfo] = React.useState(null); // Contains information on users

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
   * Returns the UI for editing users. Starts the user information fetch if we don't have it already
   * @function
   */
  function generateUsers() {
    let curUserInfo = userInfo || [];
    if (userInfo == null) {
      getUserInfo();
      setUserInfo([]);
    }
    if (curUserInfo.length <= 0) {
      return (
        <Grid container justifyContent="center" alignItems="center" sx={{position:'absolute',top:'0px', right:'0px', bottom:'0px', left:'0px'}} >
          <CircularProgress />
        </Grid>
      );
    }

    return (
      <Grid container direction="column" justifyContent="center" alignItems="center" sx={{width:'100%', overflowX:'scroll'}} >
        <Grid id="admin-settings-collection-header" container direction="row" justifyContent="space-between" alignItems="start"
              sx={{width:'100%', backgroundColor:'lightgrey', borderBottom:'1px solid black'}} >
          <Grid size={2}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Name
            </Typography>
          </Grid>
          <Grid size={3}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Email
            </Typography>
          </Grid>
          <Grid size={5}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Collections
            </Typography>
          </Grid>
          <Grid sizeo={1}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Admin
            </Typography>
          </Grid>
          <Grid sizeo={1} sx={{leftMargin:'auto'}}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Auto
            </Typography>
          </Grid>
        </Grid>
        { curUserInfo.map((item,idx) => 
            <Grid container direction="row" id={"admin-user-"+idx} key={item.name+'-'+idx} direction="row" justifyContent="space-between" alignItems="start"
                  sx={{width:'100%', '&:hover':{backgroundColor:'rgba(0,0,0,0.05)'}}} >
              <Grid size={2}>
                <Typography nowrap="true" variant="body2">
                  {item.name}
                </Typography>
              </Grid>
              <Grid size={3}>
                <Typography nowrap="true" variant="body2">
                  {item.email}
                </Typography>
              </Grid>
              <Grid size={5}>
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
              </Grid>
              <Grid size={1}>
                <Typography nowrap="true" variant="body2" align="right">
                  {item.admin ? 'Y' : ' '}
                </Typography>
              </Grid>
              <Grid size={1}>
                <Typography nowrap="true" variant="body2" align="right">
                  {item.auto ? 'Y' : 'N'}
                </Typography>
              </Grid>
            </Grid>
        )}
      </Grid>
    );
  }

  function generateCollections() {
    if (loadingCollections) {
      return (
        <Grid container justifyContent="center" alignItems="center" sx={{position:'absolute',top:'0px', right:'0px', bottom:'0px', left:'0px'}} >
          <CircularProgress />
        </Grid>
      );
    }

    return (
      <Grid container direction="column" justifyContent="center" alignItems="center" sx={{width:'100%', overflowX:'scroll'}} >
        <Grid id="admin-settings-collection-header" container direction="row" justifyContent="space-between" alignItems="start"
              sx={{width:'100%', backgroundColor:'lightgrey', borderBottom:'1px solid black'}} >
          <Grid size={5}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Name
            </Typography>
          </Grid>
          <Grid size={4} sx={{marginRight:'auto'}}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              ID
            </Typography>
          </Grid>
          <Grid sizeo={3} sx={{leftMargin:'auto'}}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              email
            </Typography>
          </Grid>
        </Grid>
        { collectionInfo.map((item, idx) => 
            <Grid container direction="row" id={"admin-species-"+idx} key={item.name+'-'+idx} direction="row" justifyContent="space-between" alignItems="start"
                  sx={{width:'100%', '&:hover':{backgroundColor:'rgba(0,0,0,0.05)'}}} >
              <Grid size={5}>
                <Typography nowrap="true" variant="body2">
                  {item.name}
                </Typography>
              </Grid>
              <Grid size={4} sx={{marginRight:'auto'}}>
                <Typography nowrap="true" variant="body2">
                  {item.id}
                </Typography>
              </Grid>
              <Grid sizeo={3} sx={{leftMargin:'auto'}}>
                <Typography nowrap="true" variant="body2">
                  {item.email}
                </Typography>
              </Grid>
          </Grid>
        )}
      </Grid>
    );
  }

  function generateSpecies() {
    let curSpecies = masterSpecies || [];
    if (masterSpecies == null) {
      getMasterSpecies();
      setMasterSpecies([]);
    }
    if (curSpecies.length <= 0) {
      return (
        <Grid container justifyContent="center" alignItems="center" sx={{position:'absolute',top:'0px', right:'0px', bottom:'0px', left:'0px'}} >
          <CircularProgress />
        </Grid>
      );
    }

    return (
      <Grid container direction="column" justifyContent="center" alignItems="center" sx={{width:'100%'}} >
        <Grid id="admin-settings-species-header" container direction="row" justifyContent="space-between" alignItems="start"
              sx={{width:'100%', backgroundColor:'lightgrey', borderBottom:'1px solid black'}} >
          <Grid size={5}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Name
            </Typography>
          </Grid>
          <Grid size={5} sx={{marginRight:'auto'}}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Scientific Name
            </Typography>
          </Grid>
          <Grid sizeo={2} sx={{leftMargin:'auto'}}>
            <Typography nowrap="true" variant="body2" sx={{fontWeight:'bold', fontSize:'initial'}}>
              Key Binding
            </Typography>
          </Grid>
        </Grid>
      { curSpecies.map((item, idx) => 
            <Grid container direction="row" id={"admin-species-"+idx} key={item.name+'-'+idx} direction="row" justifyContent="space-between" alignItems="start"
                  sx={{width:'100%', '&:hover':{backgroundColor:'rgba(0,0,0,0.05)'}}} >
              <Grid size={5}>
                <Typography nowrap="true" variant="body2">
                  {item.name}
                </Typography>
              </Grid>
              <Grid size={5} sx={{marginRight:'auto'}}>
                <Typography nowrap="true" variant="body2">
                  {item.scientificName}
                </Typography>
              </Grid>
              <Grid sizeo={2} sx={{leftMargin:'auto'}}>
                <Typography nowrap="true" variant="body2">
                  {item.keyBinding}
                </Typography>
              </Grid>
            </Grid>
      )}
      </Grid>
    );
  }

  function generateLocations() {
    if (loadingLocations) {
      return (
        <Grid container justifyContent="center" alignItems="center" sx={{position:'absolute',top:'0px', right:'0px', bottom:'0px', left:'0px'}} >
          <CircularProgress />
        </Grid>
      );
    }

    return (
      <Grid container direction="column" justifyContent="center" alignItems="center" sx={{width:'100%'}} >
        <Grid id="admin-settings-species-header" container direction="row" justifyContent="space-between" alignItems="start"
              sx={{width:'100%', backgroundColor:'lightgrey', borderBottom:'1px solid black'}} >
          <Grid size={5}>
            <Typography nowrap="true" variant="body" sx={{fontWeight:'bold'}}>
              Name
            </Typography>
          </Grid>
          <Grid size={5} sx={{marginRight:'auto'}}>
            <Typography nowrap="true" variant="body" sx={{fontWeight:'bold'}}>
              ID
            </Typography>
          </Grid>
          <Grid sizeo={2} sx={{marginLeft:'auto'}}>
            <Typography nowrap="true" variant="body" sx={{fontWeight:'bold'}}>
              Location
            </Typography>
          </Grid>
        </Grid>
      { locationItems.map((item, idx) => 
            <Grid container direction="row" id={"admin-species-"+idx} key={item.name+'-'+idx} justifyContent="space-between" alignItems="start"
                  sx={{width:'100%', '&:hover':{backgroundColor:'rgba(0,0,0,0.05)'} }} >
              <Grid size={5}>
                <Typography nowrap="true" variant="body2">
                  {item.nameProperty}
                </Typography>
              </Grid>
              <Grid size={2} sx={{marginRight:'auto'}}>
                <Typography nowrap="true" variant="body2">
                  {item.idProperty}
                </Typography>
              </Grid>
              <Grid size={5} sx={{marginLeft:'auto'}} >
                <Typography nowrap="true" variant="body2" align="right">
                  {item.latProperty + ', ' + item.lngProperty}
                </Typography>
              </Grid>
            </Grid>
      )}
      </Grid>
    );
  }

  // Setup the tab and page generation
  const adminTabs = [
    {name:'Users', uiFunc:generateUsers},
    {name:'Collections', uiFunc:generateCollections},
    {name:'Species', uiFunc:generateSpecies},
    {name:'Locations', uiFunc:generateLocations},
  ];

  const idx = 0;
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
        <Grid size={11} sx={{overflowX:'scroll',display:'flex'}} sx={{backgroundColor:'#EAEAEA', borderRadius:'0px 25px 25px 25px', overflow:'scroll', padding:'0px 25px 15px 15px'}}>
          { adminTabs.map((item,idx) => 
              <TabPanel id={'admin-settings-panel-'+item.name} key={item.name+'-'+idx}  value={activeTab} index={idx}
                        style={{width:'100%', position:'relative',margin:'0 16px auto 8px', height:uiSizes.workspace.height+'px'}}>
                <Grid container direction="column" justifyContent="center" alignItems="center" sx={{width:'100%'}} >
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
        </Grid>
      </Grid>
      </Grid>
  );
}
