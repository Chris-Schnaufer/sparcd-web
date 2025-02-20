'use client'

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

export default function ManageUploads({selectedUpload}) {
  const theme = useTheme();
  const sidebarRef = React.useRef();
  const sandboxItems = React.useContext(SandboxInfoContext);
  const [totalHeight, setTotalHeight] = React.useState(null);
  const [workingTop, setWorkingTop] = React.useState(null);
  const [sidebarWidth, setSidebarWidth] = React.useState(150);
  const [resizeDrawForce, setResizeDrawForce] = React.useReducer(o => !o); // Forcing redraw on resize (most element dimensions don't change)
  const [selectionIndex, setSelectionIndex] = React.useState(sandboxItems.findIndex((item) => item.name == selectedUpload));
  const [editing, setEditing] = React.useState(false);

  React.useLayoutEffect(() => {
      function onResize () {
          calcTotalHeight();
          if (sidebarRef.current) {
            setSidebarWidth(sidebarRef.current.offsetWidth);
          }

          setResizeDrawForce();
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  function onSandboxChange(ev, name) {
    ev.preventDefault();
    setSelectionIndex(sandboxItems.findIndex((item) => item.name == name));
  }

  function onCancelEditUpload(ev, selection) {
    ev.preventDefault();
    setSelectionIndex(-1);
  }

  function onEditUpload(ev, selection) {
    ev.preventDefault();
    setEditing(true);
  }

  function calcTotalHeight() {
    const elHeader = document.getElementById('sparcd-header');
    const elFooter = document.getElementById('sparcd-footer');
    const elHeaderSize = elHeader.getBoundingClientRect();
    const elFooterSize = elFooter.getBoundingClientRect();

    let maxHeight = (window.innerHeight - elHeaderSize.height - elFooterSize.height) + 'px';

    setTotalHeight(maxHeight);
    setWorkingTop(elHeaderSize.height);

    const elLeftSidebar = document.getElementById('left-sidebar');
    if (elLeftSidebar) {
      const elLeftSidebarSize = elLeftSidebar.getBoundingClientRect();
      setSidebarWidth(elLeftSidebarSize.width);
    }
  }

  if (totalHeight == null) {
    calcTotalHeight();
  }

  const curHeight = totalHeight;
  const curStart = workingTop + 'px';
  const workplaceStartX = sidebarWidth;
  const workplaceWidth = window.innerWidth - sidebarWidth;
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
                     'minWidth':workplaceWidth, 'maxWidth':workplaceWidth, 'width':workplaceWidth, 'position':'absolute' }}>
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
                    Do you want to edit upload <span style={{fontWeight:'bold'}}>{sandboxItems[curSelectionIndex].name}</span>?
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