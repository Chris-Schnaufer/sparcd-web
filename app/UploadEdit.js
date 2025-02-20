'use client'

import * as React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import { useTheme } from '@mui/material/styles';

import { SandboxInfoContext, SpeciesInfoContext } from './serverInfo'
import SpeciesSidebarItem from './components/SpeciesSidebarItem'

export default function UploadEdit({selectedUpload}) {
  const theme = useTheme();
  const sidebarLeftRef = React.useRef();
  const sidebarRightRef = React.useRef();
  const sandboxItems = React.useContext(SandboxInfoContext);
  const speciesItems = React.useContext(SpeciesInfoContext);
  const [sidebarWidthLeft, setSidebarWidthLeft] = React.useState(150);
  const [sidebarWidthRight, setSidebarWidthRight] = React.useState(150);
  const [workingTop, setWorkingTop] = React.useState(null);
  const [workspaceWidth, setWorkspaceWidth] = React.useState(window.innerWidth - 150); // The subtracted value is initial sidebar width
  const [totalHeight, setTotalHeight] = React.useState(null);

  React.useLayoutEffect(() => {
      function onResize () {
        calcTotalHeight();

        if (sidebarLeftRef.current) {
          setSidebarWidthLeft(sidebarLeftRef.current.offsetWidth);
        }
        if (sidebarRightRef.current) {
          setSidebarWidthRight(sidebarRightRef.current.offsetWidth);
        }

        const newWorkspaceWidth = window.innerWidth - sidebarLeftRef.current.offsetWidth
                                                    - sidebarRightRef.current.offsetWidth;
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

    let maxHeight = (window.innerHeight - elHeaderSize.height - elFooterSize.height) + 'px';

    setTotalHeight(maxHeight);
    setWorkingTop(elHeaderSize.height);

    const elLeftSidebar = document.getElementById('left-sidebar');
    if (elLeftSidebar) {
      const elLeftSidebarSize = elLeftSidebar.getBoundingClientRect();
      setSidebarWidthLeft(elLeftSidebarSize.width);
    }

    const elRightSidebar = document.getElementById('right-sidebar');
    if (elRightSidebar) {
      const elRightSidebarSize = elRightSidebar.getBoundingClientRect();
      setSidebarWidthRight(elRightSidebarSize.width);
    }
  }

  function onSpeciesChange(ev, name) {
    console.log('SPECIES CLICK:', name);
  }

  if (totalHeight == null) {
    calcTotalHeight();
  }

  const curHeight = totalHeight;
  const curStart = workingTop + 'px';
  return (
    <Box id="upload-edit"sx={{ flexGrow: 1, top:curStart, width: '100vw' }} >
      <Grid id='left-sidebar' ref={sidebarLeftRef} container direction='row' alignItems='stretch' columns='1' 
          style={{ 'minHeight':curHeight, 'maxHeight':curHeight, 'height':curHeight, 'top':curStart, 
                   'position':'absolute', 'overflow':'scroll', ...theme.palette.left_sidebar }} >
        { speciesItems.map((item, idx) => <SpeciesSidebarItem species={item} key={item.name}
                                                             onClick_func={(ev) => onSpeciesChange(ev, item.name)} />) }
      </Grid>
      <Grid id='right-sidebar' ref={sidebarRightRef} container direction='row' alignItems='stretch' columns='1' 
          style={{ 'minHeight':curHeight, 'maxHeight':curHeight, 'height':curHeight, 'top':curStart, 
                   'position':'absolute', 'overflow':'scroll', 'left':window.innerWidth-150, ...theme.palette.left_sidebar }} >
        images tree
      </Grid>
    </Box>
  );
}
