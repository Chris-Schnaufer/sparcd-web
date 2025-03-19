'use client'

/** @module CollectionsManage */

import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActionArea from '@mui/material/CardActionArea';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import CloudCircleOutlinedIcon from '@mui/icons-material/CloudCircleOutlined';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton'
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { CollectionsInfoContext, NarrowWindowContext } from './serverInfo'
import UploadSidebarItem from './components/UploadSidebarItem'

/**
 * Renders the UI for managing the list of uploaded folders
 * @function
 * @param {object} selectedCollection The currently selected collection
 * @param {function} onEditUpload Called when the user wants to edit an upload of a collection
  * @param {function} onSearchSetup Call when settting up or clearing search elements
* @returns {object} The rendered UI
 */
export default function CollectionsManage({selectedCollection, onEditUpload, onSearchSetup}) {
  const theme = useTheme();
  const sidebarRef = React.useRef();
  const collectionsItems = React.useContext(CollectionsInfoContext);
  const narrowWindow = React.useContext(NarrowWindowContext);
  const [expandedUpload, setExpandedUpload] = React.useState(false);
  const [selectionIndex, setSelectionIndex] = React.useState(collectionsItems.findIndex((item) => item.name === selectedCollection));
  const [sidebarWidth, setSidebarWidth] =  React.useState(200);// Default value is recalculated at display time
  const [totalHeight, setTotalHeight] = React.useState(null);  // Default value is recalculated at display time
  const [windowSize, setWindowSize] = React.useState({width: 640, height: 480});  // Default values are recalculated at display time
  const [workingTop, setWorkingTop] = React.useState(null);    // Default value is recalculated at display time
  const [workspaceWidth, setWorkspaceWidth] = React.useState(640);  // Default value is recalculated at display time

  const handleCollectionSearch = searchCollections.bind(CollectionsManage);

  // Setup search
  React.useEffect(() => {
    onSearchSetup('Collection Name', handleCollectionSearch);

    return () => onSearchSetup();
  }, []);

  // Recalcuate available space in the window
  React.useLayoutEffect(() => {
    const newSize = {'width':window.innerWidth,'height':window.innerHeight};
    setWindowSize(newSize);
    calcTotalSize(newSize);
    setWorkspaceWidth(newSize.width -  sidebarWidth);
  }, [narrowWindow,totalHeight,sidebarWidth]);

  // Adds a handler for when the window is resized, and automatically removes the handler
  React.useLayoutEffect(() => {
      function onResize () {
        const newSize = {'width':window.innerWidth,'height':window.innerHeight};

        setWindowSize(newSize);

        calcTotalSize(newSize);

        const newWorkspaceWidth = newSize.width - sidebarWidth;
        setWorkspaceWidth(newWorkspaceWidth);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, [narrowWindow,totalHeight,sidebarWidth]);


  /**
   * Searches for collections that meet the search criteria and scrolls it into view
   * @function
   * @param {string} searchTerm The term to search in a collection
   */
  function searchCollections(searchTerm) {
    const ucSearchTerm = searchTerm.toUpperCase();
    const foundCollections = collectionsItems.filter((item) => item.name.toUpperCase().includes(ucSearchTerm) ||
                                                               item.description.toUpperCase().includes(ucSearchTerm));

    if (foundCollections) {
      console.log('FOUND', foundCollections);
    }
  }

  /**
   * Returns a function that will set the expanded panel name for Accordian panels
   * @function
   * @param {string} panelName Unique identifier of the panel
   * @returns {function} A function that will handle the accordian state change
   */
  function handleExpandedChange(panelName) {
    return (event, isExpanded) => {
      setExpandedUpload(isExpanded ? panelName : false);
    }
  }

  /**
   * Handler for when the user's selection changes and prevents default behavior
   * @function
   * @param {object} event The event
   * @param {string} bucket The bucket of the new selected collection
   * @param {string} id The ID of the new selected collection
   */
  function onCollectionChange(event, bucket, id) {
    event.preventDefault();
    setSelectionIndex(collectionsItems.findIndex((item) => item.bucket === bucket && item.id === id));
  }

  /**
   * Calculates the total UI size available for the workarea
   * @function
   * @param {object} curSize The total width and height of the window
   */
  function calcTotalSize(curSize) {
    const elWorkspace = document.getElementById('image-edit-workspace-wrapper');
    if (elWorkspace) {
      const elWorkspaceSize = elWorkspace.getBoundingClientRect();
      setTotalHeight(elWorkspaceSize.height);
      setWorkingTop(0);
    }

    let curSidebarWidth = 0;
    if (sidebarRef.current) {
      curSidebarWidth = sidebarRef.current.offsetWidth;
      setSidebarWidth(curSidebarWidth);
    }

    setWorkspaceWidth(curSize.width - curSidebarWidth);
  }

  // Render the UI
  const curHeight = (totalHeight || 480) + 'px';
  const curStart = (workingTop || 25) + 'px';
  const curSelectionIndex = selectionIndex;
  const curCollection = collectionsItems[curSelectionIndex] || {uploads: []};
  return (
    <Box id='image-edit-workspace-wrapper' sx={{ flexGrow: 1, 'width': '100vw', position:'relative' }} >
      <Grid id='collection-workspace-details' ref={sidebarRef} container direction="column" alignItems="start" justifyContent="start"
            sx={{position:'absolute', top:'0px', width:'40vw', minHeight:curHeight, maxHeight:curHeight, right:'-0', backgroundColor:'white',
                 borderLeft:'1px solid grey', overflow:'scroll'}}
      >
        { curCollection.uploads.map((item, idx) =>
          <Card id={name} key={'collection-upload-'+idx} variant="outlined" sx={{minWidth:'100%', '&:hover':{backgroundColor:theme.palette.action.active} }}>
            <CardHeader title={
                              <Grid id="card-header-wrapper" container direction="row" alignItems="start" justifyContent="start">
                                <Grid item>
                                  <Typography gutterBottom variant="h6" component="h4">
                                    {item.name}
                                  </Typography>
                                </Grid>
                                <Grid item sx={{marginLeft:'auto'}}>
                                  <Tooltip title="Edit this upload">
                                    <IconButton aria-label="Edit this upload" onClick={() => onEditUpload(curCollection.id, item.name)}>
                                      <CloudCircleOutlinedIcon fontSize="small"/>
                                    </IconButton>
                                  </Tooltip>
                                </Grid>
                              </Grid>
                              }
                          style={{paddingBottom:'0px'}}
            />
            <CardContent sx={{paddingTop:'0px'}}>
              <Accordion expanded={expandedUpload === 'upload-details-'+item.name}
                         onChange={handleExpandedChange('upload-details-'+item.name)}>
                <AccordionSummary
                  id={'summary-'+item.name}
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls="upload-details-content"
                >
                  <Typography component="span">
                    Advanced details
                  </Typography>
                </AccordionSummary>
                <AccordionDetails sx={{backgroundColor:'darkgrey'}}>
                  <Grid container id={'collection-upload-'+item.name} direction="column" alignItems="start" justifyContent="start">
                    <Grid item sx={{padding:'5px 0'}}>
                      <Typography variant="body2">
                        {item.imagesCount + '/' + item.imagesWithSpeciesCount + 'images tagged with species'}
                      </Typography>
                    </Grid>
                    <Grid item sx={{padding:'5px 0'}}>
                      <Typography variant="body2">
                        {item.description}
                      </Typography>
                    </Grid>
                    <Grid item>
                      <Typography variant="body2" sx={{fontWeight:'500'}}>
                        Edits
                      </Typography>
                    </Grid>
                  </Grid>
                  <Box sx={{border:"1px solid black", width:'100%', minHeight:'4em', maxHeight:'4em', overflow:"scroll"}} >
                    {item.edits.map((editItem, idx) =>
                      <Typography variant="body2" key={"collection-upload-edits-" + idx} sx={{padding:"0 5px"}} >
                        {editItem.name + ' ' + editItem.date}
                      </Typography>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        )}
      </Grid>
      <Grid id='collection-workspace' container direction="row" alignItems="start" justifyContent="start"
            columnSpacing={2}
            rowSpacing={1}
            style={{ position:'absolute',
                     top: '0px',
                     maxWidth:workspaceWidth + 'px',
                     minWidth:workspaceWidth + 'px',
                     maxHeight:curHeight,
                     paddingTop: '10px',
                     overflow:'scroll',
                     margin: '0px'}}
        >
        { collectionsItems.map((item, idx) =>
          <Grid item key={'collection-'+item.name} size={{ xs: 12, sm: 12, md:12 }}>
                <Grid display='flex' justifyContent='left' size='grow' >
                  <Card id={item.name} onClick={(event) => onCollectionChange(event, item.bucket, item.id)} variant="outlined"
                        sx={{minWidth:'200px', '&:hover':{backgroundColor:theme.palette.action.active} }}>
                    <CardActionArea data-active={selectionIndex === idx ? '' : undefined}
                      sx={{height: '100%', '&[data-active]': {backgroundColor:theme.palette.action.active} }}
                    >
                      <CardContent>
                        <Grid container direction="column" spacing={1}>
                          <Grid item>
                            <Typography variant="body">
                              {item.name}
                            </Typography>
                          </Grid>
                          <Grid item>
                            <Typography variant="body">
                              {item.organization}
                            </Typography>
                          </Grid>
                          <Grid item>
                            <Typography variant="body">
                              {item.email}
                            </Typography>
                          </Grid>
                          <Grid item>
                            <Typography variant="body">
                              {item.description}
                            </Typography>
                          </Grid>
                        </Grid>
                        <Typography variant="body3">
                          Uploads
                        </Typography>
                        <Box sx={{border:"1px solid black", width:"100%", minHeight:'3em', maxHeight:'3em', overflow:"scroll"}} >
                          {item.uploads.map((uploadItem) =>
                              <Grid container key={"upload-"+uploadItem.name} direction="column" spacing={1}>
                                <Grid item>
                                  <Typography variant="body" sx={{padding:"0 5px"}}>
                                    {uploadItem.name}
                                  </Typography>
                                </Grid>
                              </Grid>
                          )}
                        </Box>
                      </CardContent>
                    </CardActionArea>
                  </Card>
                </Grid>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
