/** @module components/EditUser */

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

import { AddMessageContext } from '../serverInfo';
import { Level } from './Messages';

/**
 * Handles editing a user's entry
 * @function
 * @param {object} {data} The user's data. If falsy a new user is assumed
 * @param {function} onUpdate Called to update the user information when changes made
 * @param {function} onClose Called when the editing is completed
 * @return {object} The UI for editing users
 */
export default function EditUser({data, onUpdate, onClose}) {
  const theme = useTheme();
  const addMessage = React.useContext(AddMessageContext); // Function adds messages for display
  const [isModified, setIsModified] = React.useState(false);
  const [userName, setUserName] = React.useState(data ? data.name : null);
  const [userEmail, setUserEmail] = React.useState(data ? data.email : null);

  /**
   * Handles saving the changes to the user
   * @function
   */
  function onSaveChanges() {
    if (!isModified) {
      return;
    }

    // Save the edited user data
    let updatedData = data ? JSON.parse(JSON.stringify(data)) : {};

    let el = document.getElementById('edit-user-name');
    if (el) {
      updatedData.name = el.value;
    }

    el = document.getElementById('edit-user-email');
    if (el) {
      updatedData.email = el.value;
    }

    onUpdate(updatedData, onClose, (message) => addMessage(Level.Warning, message));
  }

  /**
   * Generates the collections UI for editing the user
   * @function
   * @return {object} the UI for editing user collections
   */
  function generateCollections() {
    return (
      <Grid container direction="column" justifyContent="start" alignItems="stretch" sx={{borderTop:'1px solid black'}} >
          <Grid container key={'user-edit-coll-titles'} direction="row" justifyContent="space-between" alignItems="center"
                sx={{backgroundColor:'lightgrey', height:'1.5em'}} >
            <Grid size={{sm:9}} >
              <Typography nowrap="true" align="start" component="div">
                <Box sx={{ fontWeight: 'bold', paddingLeft:'5px' }}>
                Collection
                </Box>
              </Typography>
            </Grid>
            <Grid size={{sm:1}} >
              <Typography nowrap="true" align="center" component="div">
                <Box sx={{ fontWeight: 'bold' }}>
                R
                </Box>
              </Typography>
            </Grid>
            <Grid size={{sm:1}} >
              <Typography nowrap="true" align="center" component="div">
                <Box sx={{ fontWeight: 'bold' }}>
                W
                </Box>
              </Typography>
            </Grid>
            <Grid size={{sm:1}}  >
              <Typography nowrap="true" align="center" component="div" sx={{paddingRight:'5px'}}>
                <Box sx={{ fontWeight: 'bold' }}>
                O
                </Box>
              </Typography>
            </Grid>
          </Grid>
        { data.collections.map((item) =>
          <Grid container key={'user-edit-coll-'+item.id} direction="row" justifyContent="space-between" alignItems="center" sx={{height:'2em'}}>
            <Grid size={{sm:9}} sx={{paddingLeft:'5px'}} >
              <Typography variant="body2">
              {item.name}
              </Typography>
            </Grid>
            <Grid size={{sm:1}}  >
              <Typography variant="body2" align="center">
              <Checkbox disabled size="small" checked={!!item.read} onChange={() => setIsModified(true)}/>
              </Typography>
            </Grid>
            <Grid size={{sm:1}}  >
              <Typography variant="body2" align="center">
              <Checkbox disabled size="small" checked={!!item.write} onChange={() => setIsModified(true)}/>
              </Typography>
            </Grid>
            <Grid size={{sm:1}}  >
              <Typography variant="body2" align="center" sx={{paddingRight:'5px'}}>
              <Checkbox disabled size="small" checked={!!item.owner} onChange={() => setIsModified(true)}/>
              </Typography>
            </Grid>
          </Grid>
        )}
      </Grid>
    );
  }

  return (
   <Grid sx={{minWidth:'50vw'}} > 
    <Card id="edit-user" sx={{backgroundColor:'#EFEFEF', border:"none", boxShadow:"none"}} >
      <CardHeader id='edit-user-header' title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          Edit User
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
      <CardContent id='edit-user-details' sx={{paddingTop:'0px', paddingBottom:'0px'}}>
        <Grid container direction="column" justifyContent="start" alignItems="stretch"
              sx={{minWidth:'400px', border:'1px solid black', borderRadius:'5px', backgroundColor:'rgb(255,255,255,0.3)' }}>
          <TextField required disabled
                id='edit-user-name'
                label="S3 User Name"
                defaultValue={userName}
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
                id='edit-user-email'
                label="User's email address"
                defaultValue={userEmail}
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
            <FormControlLabel key={'edit-user-admin'} sx={{paddingLeft:'10px'}}
                              control={<Checkbox disabled 
                                                 size="small" 
                                                 checked={data ? data.admin : false}
                                        />} 
                              label={<Typography variant="body2">Has administrative rights</Typography>} />
            {generateCollections()}
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