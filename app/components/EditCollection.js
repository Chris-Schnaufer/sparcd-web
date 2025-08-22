/** @module components/EditCollection */

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Checkbox from '@mui/material/Checkbox';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { AddMessageContext, DefaultImageIconURL } from '../serverInfo';
import { Level } from './Messages';

/**
 * Handles editing a collection' entry
 * @function
 * @param {object} {data} The collection data. If falsy a new collection is assumed
 * @param {function} onUpdate Called to update the collection information when changes made
 * @param {function} onClose Called when the editing is completed
 * @return {object} The UI for editing collection
 */
export default function EditCollection({data, onUpdate, onClose}) {
  const theme = useTheme();
  const addMessage = React.useContext(AddMessageContext); // Function adds messages for display
  const [isModified, setIsModified] = React.useState(false);

  /**
   * Handles saving the changes to the user
   * @function
   */
  function onSaveChanges() {
    console.log('HACK:IS MODIFIED:',isModified, data);
    if (!isModified) {
      return;
    }

    // Save the edited collection data
    let updatedData = data ? JSON.parse(JSON.stringify(data)) : {};

    let el = document.getElementById('edit-collection-name');
    if (el) {
      updatedData.name = el.value;
      if (updatedData.name.length < 3) {
        addMessage(Level.Warning, "Please enter a longer name")
        el.focus();
        return;
      }
    }

    el = document.getElementById('edit-collection-scientific');
    if (el) {
      updatedData.scientificName = el.value;
      if (updatedData.scientificName.length <= 0) {
        addMessage(Level.Warning, "Please enter a scientific name")
        el.focus();
        return;
      }
    }

    el = document.getElementById('edit-collection-keybind');
    if (el) {
      updatedData.keyBinding = el.value;
    }

    el = document.getElementById('edit-collection-url');
    if (el) {
      updatedData.collectionIconURL = el.value;
      if (!updatedData.collectionIconURL) {
        updatedData.collectionIconURL = DefaultImageIconURL;
      }
    }

    onUpdate(updatedData, onClose, (message) => addMessage(Level.Warning, message));
  }

  /**
   * Generates the permissions UI
   * @function
   * @return {object} The UI for editing permissions
   */
  function generatePermissions() {
    let allPermissions = data.allPermissions ? data.allPermissions : [data.permissions];
    const isOwner = data.permissions ? data.permissions.ownerProperty : false;

    if (!allPermissions || (allPermissions.length == 1 && allPermissions[0] === null)) {
      console.log('HACK:     CAUGHT');
      return (
        <Typography gutterBottom variant="body3" noWrap="true" sx={{paddingLeft:'10px'}} >
          No permissions available to edit
        </Typography>
      );
    }

    return (
      <Grid id="edit-collection-permissions-wrapper" container direction="column" alignItems="stretch" justifyContent="start" >
        <Grid container key={'user-edit-coll-titles'} direction="row" justifyContent="space-between" alignItems="center"
              sx={{backgroundColor:'lightgrey', height:'1.5em'}} >
          <Grid size={{sm:9}} >
            <Typography variant="body2" nowrap="true" align="start" component="div">
              <Box sx={{ fontWeight: 'bold', paddingLeft:'10px' }}>
              User Name
              </Box>
            </Typography>
          </Grid>
          <Grid size={{sm:1}} >
            <Typography variant="body2" nowrap="true" align="center" component="div">
              <Box sx={{ fontWeight: 'bold' }}>
              R
              </Box>
            </Typography>
          </Grid>
          <Grid size={{sm:1}} >
            <Typography variant="body2" nowrap="true" align="center" component="div">
              <Box sx={{ fontWeight: 'bold' }}>
              W
              </Box>
            </Typography>
          </Grid>
          <Grid size={{sm:1}}  >
            <Typography variant="body2" nowrap="true" align="center" component="div" sx={{paddingRight:'5px'}}>
              <Box sx={{ fontWeight: 'bold' }}>
              O
              </Box>
            </Typography>
          </Grid>
        </Grid>
        { allPermissions.map((item, idx) =>
          <Grid id={"edit-collection-permission-" + item.name} key={"collection-"+item.name} container direction="row">
            <Grid size={{sm:9}} sx={{paddingLeft:'10px'}} >
              <Typography variant="body2">
              {item.usernameProperty}
              </Typography>
            </Grid>
            <Grid size={{sm:1}}  >
              <Typography variant="body2" align="center">
              <Checkbox disabled={!isOwner} size="small" checked={!!item.readProperty} onChange={() => setIsModified(true)}/>
              </Typography>
            </Grid>
            <Grid size={{sm:1}}  >
              <Typography variant="body2" align="center">
              <Checkbox disabled={!isOwner} size="small" checked={!!item.uploadProperty} onChange={() => setIsModified(true)}/>
              </Typography>
            </Grid>
            <Grid size={{sm:1}}  >
              <Typography variant="body2" align="center" sx={{paddingRight:'5px'}}>
              <Checkbox disabled={!isOwner} size="small" checked={!!item.ownerProperty} onChange={() => setIsModified(true)}/>
              </Typography>
            </Grid>
          </Grid>
        )}
      </Grid>
    );
  }

  return (
   <Grid sx={{minWidth:'50vw'}} > 
    <Card id="edit-collection" sx={{backgroundColor:'#EFEFEF', border:"none", boxShadow:"none"}} >
      <CardHeader id='edit-collection-header' title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          Edit Collection
                        </Typography>
                      </Grid>
                      <Grid sx={{marginLeft:'auto'}} >
                        <div onClick={onClose}>
                          <Tooltip title="Close without saving">
                            <Typography gutterBottom variant="body2" noWrap="true"
                                        sx={{textTransform:'uppercase',
                                        color:'grey',
                                        cursor:'pointer',
                                        fontWeight:'500',
                                        backgroundColor:'rgba(0,0,0,0.03)',
                                        padding:'3px 3px 3px 3px',
                                        borderRadius:'3px',
                                        '&:hover':{backgroundColor:'rgba(255,255,255,0.7)', color:'black'}
                                     }}
                            >
                                <CloseOutlinedIcon size="small" />
                            </Typography>
                          </Tooltip>
                        </div>
                      </Grid>
                    </Grid>
                    }
                style={{paddingTop:'0px', paddingBottom:'0px'}}
      />
      <CardContent id='edit-collection-details' sx={{paddingTop:'0px', paddingBottom:'0px'}}>
        <Grid container direction="column" justifyContent="start" alignItems="stretch"
              sx={{minWidth:'400px', border:'1px solid black', borderRadius:'5px', backgroundColor:'rgb(255,255,255,0.3)' }}>
          <TextField disabled={!!data}
                id='edit-collection-id'
                label="ID"
                defaultValue={data ? data.id : null}
                size='small'
                disabled={true}
                sx={{margin:'10px'}}
                onChange={() => setIsModified(true)}
                inputProps={{style: {fontSize: 12}}}
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                />
          <TextField required
                id='edit-collection-name'
                label="Name"
                defaultValue={data ? data.name : null}
                size='small'
                sx={{margin:'10px'}}
                onChange={() => setIsModified(true)}
                inputProps={{style: {fontSize: 12}}}
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                />
          <TextField 
                id='edit-collection-organization'
                label="Organization"
                defaultValue={data ? data.organization : null}
                size='small'
                sx={{margin:'10px'}}
                onChange={() => setIsModified(true)}
                inputProps={{style: {fontSize: 12}}}
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                />
          <TextField 
                id='edit-collection-description'
                label="Description"
                type='url'
                defaultValue={data ? data.description : null}
                size='small'
                sx={{margin:'10px'}}
                multiline
                rows={3}
                onChange={() => setIsModified(true)}
                inputProps={{style: {fontSize: 12}}}
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                />
          <TextField 
                id='edit-collection-email'
                label="Email"
                defaultValue={data ? data.email : null}
                size='small'
                type="email"
                sx={{margin:'10px'}}
                onChange={() => setIsModified(true)}
                inputProps={{style: {fontSize: 12}}}
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                />
          <Typography gutterBottom variant="body" noWrap="true" sx={{fontWeigth:'bold', paddingLeft:'10px'}} >
            Permissions
          </Typography>
          { generatePermissions() }
       </Grid>          
        </CardContent>
        <CardActions id='filter-content-actions'>
          <Button sx={{flex:'1', disabled:isModified === false }} onClick={onSaveChanges}>Save</Button>
          <Button sx={{flex:'1'}} onClick={onClose} >Cancel</Button>
        </CardActions>
    </Card>
  </Grid>
  );
}