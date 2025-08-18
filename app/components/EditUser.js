/** @module components/Settings */

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
  const [userName, setUserName] = React.useState(data ? data.name : null);
  const [userEmail, setUserEmail] = React.useState(data ? data.email : null);
  const [userAdmin, setUserAdmin] = React.useState(data ? data.admin : false);

  const isModified = false;

  /**
   * Handles saving the changes to the user
   * @function
   */
  function onSaveChanges() {
    // Save the edited user data
    // onUpdate(data, onClose, () => {})
  }

  /**
   * Handles the admin checkbox changing
   * @functino
   * @param {object} event The triggering event
   */
  function handleAdminChange(event) {
    setUserAdmin(event.target.checked);
    setIsModified(true);
  }

  /**
   * Generates the collections UI for editing the user
   * @function
   * @return {object} the UI for editing user collections
   */
  function generateCollections() {
    return (
      <Grid container direction="column" justifyContent="start" alignItems="stretch" sx={{padding:'0px 15px 10px 10px'}} >
        { data.collections.map((item) =>
          <Grid container key={'user-edit-coll-'+item.id} direction="row" justifyContent="space-between" alignItems="center">
            <Grid sx={{width:'80%'}} >
              <Typography variant="body2" >
              {item.name}
              </Typography>
            </Grid>
            <Grid sm={1} >
              <Typography variant="body2" >
              {item.read ? 'Y' : 'N'}
              </Typography>
            </Grid>
            <Grid sm={1} >
              <Typography variant="body2" >
              {item.write ? 'Y' : 'N'}
              </Typography>
            </Grid>
            <Grid sm={1} >
              <Typography variant="body2" >
              {item.owner ? 'Y' : 'N'}
              </Typography>
            </Grid>
          </Grid>
        )}
      </Grid>
    );
  }

  return (
   <Grid> 
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
              sx={{minWidth:'400px', border:'1px solid black', borderRadius:'5px', paddingLeft:'5px', backgroundColor:'rgb(255,255,255,0.3)' }}>
          <TextField required 
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
                              control={<Checkbox size="small" 
                                                 checked={userAdmin}
                                                 onChange={(event) => handleAdminChange(event)}
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