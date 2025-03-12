'use client'

/** @module UploadManage */

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { SandboxInfoContext } from './serverInfo'
import UploadSidebarItem from './components/UploadSidebarItem'

/**
 * Renders the UI for managing the list of uploaded folders
 * @function
 * @param {object} selectedUpload The currently selected upload
 * @param {function} onEdit_func The to call when the user want's to edit the selected upload
 * @returns The rendered UI
 */
export default function UploadManage({selectedUpload, onEdit_func}) {
  const theme = useTheme();
  const sidebarRef = React.useRef();
  const sandboxItems = React.useContext(SandboxInfoContext);
  const [sidebarWidth, setSidebarWidth] = React.useState(150);  // Default value is recalculated at display time
  const [totalHeight, setTotalHeight] = React.useState(null);  // Default value is recalculated at display time
  const [workingTop, setWorkingTop] = React.useState(null);  // Default value is recalculated at display time
  const [workspaceWidth, setWorkspaceWidth] = React.useState(640);  // Default value is recalculated at display time
  const [selectionIndex, setSelectionIndex] = React.useState(sandboxItems.findIndex((item) => item.name == selectedUpload));
  const [windowSize, setWindowSize] = React.useState({width: 640, height: 480});  // Default values are recalculated at display time

  // Recalcuate available space in the window
  React.useLayoutEffect(() => {
    const newSize = {'width':window.innerWidth,'height':window.innerHeight};
    setWorkspaceWidth(newSize.width - 150);
    setWindowSize(newSize);
    calcTotalSize(newSize);
  }, []);

  // Adds a handler for when the window is resized, and automatically removes the handler
  React.useLayoutEffect(() => {
      function onResize () {
        const oldWorkspaceWidth = workspaceWidth;
        const newSize = {'width':window.innerWidth,'height':window.innerHeight};

        setWindowSize(newSize);

        calcTotalSize(newSize);
        if (sidebarRef.current) {
          setSidebarWidth(sidebarRef.current.offsetWidth);
        }

        const newWorkspaceWidth = newSize.width - sidebarRef.current.offsetWidth;
        setWorkspaceWidth(newWorkspaceWidth);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  /**
   * Handler for when the user's selection changes and prevents default behavior
   * @function
   * @param {object} event The event
   * @param {string} name The name of the new selected upload
   */
  function onSandboxChange(event, name) {
    event.preventDefault();
    setSelectionIndex(sandboxItems.findIndex((item) => item.name == name));
  }

  /**
   * Handles the user not wanting to edit an upload and prevents default behavior
   * @function
   * @param {object} event The event
   */
  function onCancelEditUpload(event) {
    event.preventDefault();
    setSelectionIndex(-1);
  }

  /**
   * Handle the user wanting to edit an upload  and prevents default behavior
   * @function
   * @param {object} event The event
   */
  function onEditUpload(event) {
    event.preventDefault();
    onEdit_func(sandboxItems[selectionIndex].name);
  }

  /**
   * Calculates the total UI size available for the workarea
   * @function
   * @param {object} curSize The total width and height of the window
   */
  function calcTotalSize(curSize) {
    const elHeader = document.getElementById('sparcd-header');
    const elFooter = document.getElementById('sparcd-footer');
    const elHeaderSize = elHeader.getBoundingClientRect();
    const elFooterSize = elFooter.getBoundingClientRect();

    let maxHeight = (curSize.height - elHeaderSize.height - elFooterSize.height) + 'px';
  
    setTotalHeight(maxHeight);
    setWorkingTop(elHeaderSize.height);

    const elLeftSidebar = document.getElementById('left-sidebar');
    if (elLeftSidebar) {
      const elLeftSidebarSize = elLeftSidebar.getBoundingClientRect();
      setSidebarWidth(elLeftSidebarSize.width);
    }
  }

  // Get the available workspace size if we don't have it already
  if (!totalHeight) {
    calcTotalSize(windowSize);
    setWorkspaceWidth(windowSize.width - sidebarWidth);
  }

  // Render the UI
  const curHeight = totalHeight || 480;
  const curStart = (workingTop || 25) + 'px';
  const workplaceStartX = sidebarWidth;
  const curSelectionIndex = selectionIndex;
  return (
    <Box sx={{ flexGrow: 1, 'width': '100vw' }} >
      <Grid id='left-sidebar' ref={sidebarRef} container direction='column' alignItems='stretch' columns='1' 
          style={{ 'minHeight':curHeight, 'maxHeight':curHeight, 'height':curHeight, 'top':curStart, 
                   'position':'absolute', ...theme.palette.left_sidebar }} >
        { sandboxItems.map((item, idx) => <UploadSidebarItem uploadItem={item} key={item.name} selected={idx == curSelectionIndex}
                                                             onClick_func={(ev) => onSandboxChange(ev, item.name)} />) }
      </Grid>
      <Grid id='upload-workspace' container spacing={0} direction="column" alignItems="center" justifyContent="center"
            style={{ 'minHeight':curHeight, 'maxHeight':curHeight, 'height':curHeight, 'top':curStart, 'left':workplaceStartX,
                     'minWidth':workspaceWidth, 'maxWidth':workspaceWidth, 'width':workspaceWidth, 'position':'absolute' }}>
        { curSelectionIndex <= -1 ?
            <Grid item size={{ xs: 12, sm: 12, md:12 }}>
              <Container sx={{border:'1px solid grey', borderRadius:'5px', color:'darkslategrey', background:'#E0F0E0'}}>
                <Typography variant="body" sx={{ color: 'text.secondary' }}>
                  Please select an upload to work with
                </Typography>
              </Container>
            </Grid>
          :
            <Grid item size={{ xs: 12, sm: 12, md:12 }}>
              <Card variant='outlined' sx={{backgroundColor: 'action.selected', maxWidth:'50vw'}}>
                <CardContent>
                  <Typography variant="body" sx={{ color: 'text.secondary' }}>
                    Do you want to edit <span style={{fontWeight:'bold'}}>{sandboxItems[curSelectionIndex].name}</span>?
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button sx={{'flex':'1'}} size="small" onClick={onEditUpload} >Edit</Button>
                  <Button sx={{'flex':'1'}} size="small"onClick={onCancelEditUpload} >Cancel</Button>
                </CardActions>
              </Card>
            </Grid>
        }
      </Grid>
    </Box>
  );
}
