'use client'

import * as React from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Container from '@mui/material/Container';
import FormControl from '@mui/material/FormControl';
import Grid from '@mui/material/Grid';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { LocationsInfoContext, SandboxInfoContext, SpeciesInfoContext } from './serverInfo'
import SpeciesSidebarItem from './components/SpeciesSidebarItem'

export default function UploadEdit({selectedUpload, onCancel_func}) {
  const theme = useTheme();
  const sidebarLeftRef = React.useRef();
  const sidebarRightRef = React.useRef();
  const sandboxItems = React.useContext(SandboxInfoContext);
  const speciesItems = React.useContext(SpeciesInfoContext);
  const locationItems = React.useContext(LocationsInfoContext);
  const curUpload = sandboxItems.find((item) => item.name == selectedUpload);
  const [editingImages, setEditingImages] = React.useState(false);
  const [sidebarWidthLeft, setSidebarWidthLeft] = React.useState(150);
  const [sidebarWidthRight, setSidebarWidthRight] = React.useState(150);
  const [workingTop, setWorkingTop] = React.useState(null);
  const [workspaceWidth, setWorkspaceWidth] = React.useState(150); // The subtracted value is initial sidebar width
  const [totalHeight, setTotalHeight] = React.useState(null);

  React.useLayoutEffect(() => {
    setWorkspaceWidth(window.innerWidth - 150);
  })

  React.useLayoutEffect(() => {
      function onResize () {
        calcTotalHeight();
        let leftWidth = 0;
        let rightWidth = 0;

        if (sidebarLeftRef && sidebarLeftRef.current) {
          leftWidth = sidebarLeftRef.current.offsetWidth;
          setSidebarWidthLeft(leftWidth);
        }
        if (sidebarRightRef && sidebarRightRef.current) {
          rightWidth = sidebarRightRef.current.offsetWidth;
          setSidebarWidthRight(rightWidth);
        }

        const newWorkspaceWidth = window.innerWidth - leftWidth - rightWidth;
        console.log('NewWidth',newWorkspaceWidth);
        setWorkspaceWidth(newWorkspaceWidth);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  function calcTotalHeight() {
    const elHeader = document.getElementById('sparcd-header');
    const elFooter = document.getElementById('sparcd-footer');
    const elHeaderSize = elHeader.getBoundingClientRect();
    const elFooterSize = elFooter.getBoundingClientRect();

    let maxHeight = '100px';
    if (typeof window !== "undefined") {
      maxHeight = (window.innerHeight - elHeaderSize.height - elFooterSize.height) + 'px';
    }

    setTotalHeight(maxHeight);
    setWorkingTop(elHeaderSize.height);

    const elLeftSidebar = document.getElementById('left-sidebar');
    if (elLeftSidebar) {
      const elLeftSidebarSize = elLeftSidebar.getBoundingClientRect();
      setSidebarWidthLeft(elLeftSidebarSize.width);
    }

    const elRightSidebar = document.getElementById('right-sidebar');
    if (elRightSidebar) {
      if (elRightSidebar.style.visibility != 'hidden') {
        const elRightSidebarSize = elRightSidebar.getBoundingClientRect();
        setSidebarWidthRight(elRightSidebarSize.width);
      } else {
        setSidebarWidthRight(0);
      }
    }
  }

  function onContinue(ev) {
    console.log('Continue:');
  }

  function onCancel(ev) {
    onCancel_func();
  }

  function onKeybindClick(ev, name, oldKeybinding) {
    console.log('SPECIES CLICK:', name, oldKeybinding);
  }

  if (totalHeight == null) {
    calcTotalHeight();
  }

  const curHeight = totalHeight;
  const curStart = workingTop + 'px';
  const workplaceStartX = sidebarWidthLeft;
  let rightSidebarLeft = '150px';
  if (typeof window != "undefined") {
    rightSidebarLeft = window.innerWidth - theme.palette.right_sidebar.maxWidth;
  }

  return (
    <Box id="upload-edit"sx={{ flexGrow: 1, top:curStart, width: '100vw' }} >
      <Grid id='left-sidebar' ref={sidebarLeftRef} container direction='row' alignItems='stretch' columns='1' 
          style={{ 'minHeight':curHeight, 'maxHeight':curHeight, 'height':curHeight, 'top':curStart, 
                   'position':'absolute', 'overflow':'scroll', ...theme.palette.species_left_sidebar }} >
        { speciesItems.map((item, idx) => <SpeciesSidebarItem species={item} key={item.name}
                                                             onClick_func={(ev) => onKeybindClick(ev, item.name, item.keyBinding)} />) }
      </Grid>
      <Grid id='image-edit-workspace' container spacing={0} direction="column" alignItems="center" justifyContent="center"
            style={{ 'minHeight':curHeight, 'maxHeight':curHeight, 'height':curHeight, 'top':curStart, 'left':workplaceStartX,
                     'minWidth':workspaceWidth, 'maxWidth':workspaceWidth, 'width':workspaceWidth, 'position':'absolute' }}>
        <Grid item size={{ xs: 12, sm: 12, md:12 }}>
          <Card id='testing' variant='outlined' sx={{backgroundColor:'action.selected', minWidth:'30vw', maxWidth:'50vw'}}>
            <CardContent>
              <Typography variant="h5" sx={{ color:'text.primary', textAlign:'center' }}>
                {curUpload.name}
              </Typography>
              <FormControl fullWidth>
                <Autocomplete
                  options={locationItems}
                  id="upload-edit-location"
                  autoHighlight
                  getOptionLabel={(option) => option.idProperty}
                  getOptionKey={(option) => option.idProperty+option.latProperty+option.lngProperty}
                  onChange={() => console.log('CHANGE')}
                  renderOption={(props, loc) => {
                    const { key, ...optionProps } = props;
                    { return (<MenuItem value={loc.idProperty} key={key} {...optionProps}>
                              <Grid container>
                              <Grid item sm={6} md={6} lg={6}>
                              <Box display="flex" justifyContent="flex-start">
                                {loc.idProperty }
                              </Box>
                              </Grid>
                              <Grid item sm={6} md={6} lg={6}>
                              <Box display="flex" justifyContent="flex-end">
                              <Typography variant="body" sx={{ fontSize:'smaller'}}>
                                {'(' + loc.latProperty + ', ' + loc.lngProperty + ')'}
                              </Typography>
                              </Box>
                              </Grid>
                              </Grid>
                              </MenuItem> 
                            );
                    }
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Location"
                      slotProps={{
                        htmlInput: {
                          ...params.inputProps,
                          autoComplete: 'new-password', // disable autocomplete and autofill
                        },
                      }}
                    />
                  )}
                >
                </Autocomplete>
              </FormControl>
            </CardContent>
            <CardActions>
              <Button sx={{'flex':'1'}} size="small" onClick={onContinue} >Continue</Button>
              <Button sx={{'flex':'1'}} size="small" onClick={onCancel} >Cancel</Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>
      { editingImages ? 
          <Grid id='right-sidebar' ref={sidebarRightRef} container direction='row' alignItems='stretch' columns='1' 
              style={{ 'minHeight':curHeight, 'maxHeight':curHeight, 'height':curHeight, 'top':curStart, 
                       'visibility':(editingImages ? 'visible':'hidden'), 'position':'absolute', 'overflow':'scroll',
                       'left':rightSidebarLeft, ...theme.palette.right_sidebar }} >
            images tree
          </Grid>
        : null
      }
    </Box>
  );
}
