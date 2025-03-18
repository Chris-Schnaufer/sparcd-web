/** @module UploadEdit */

'use client'

import * as React from 'react';
import BorderColorOutlinedIcon from '@mui/icons-material/BorderColorOutlined';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { LocationsInfoContext, NarrowWindowContext, SandboxInfoContext, SpeciesInfoContext } from './serverInfo'
import ImageEdit from './ImageEdit'
import ImageTile from './components/ImageTile'
import LocationSelection from './LocationSelection'
import SpeciesKeybind from './components/SpeciesKeybind'
import SpeciesSidebar from './components/SpeciesSidebar'
import SpeciesSidebarItem from './components/SpeciesSidebarItem'
import * as utils from './utils'

/**
 * Handles editing an upload from a collection
 * @function
 * @param {object} selectedUpload The active upload to edit
 * @param {function} onCancel Call when finished with the the upload edit
 * @param {function} onSearchSetup Call when settting up or clearing search elements
 * @returns {object} The UI to render
 */
export default function UploadEdit({selectedUpload, onCancel, onSearchSetup}) {
  const theme = useTheme();
  const editingStates = {'none':0, 'listImages':2, 'editImage': 3}; // Different states of this page
  const sidebarSpeciesRef = React.useRef();  // Used for sizeing
  const sidebarTopRef = React.useRef();   // Used for sizeing
  const sandboxItems = React.useContext(SandboxInfoContext);
  const speciesItems = React.useContext(SpeciesInfoContext);
  const locationItems = React.useContext(LocationsInfoContext);
  const narrowWindow = React.useContext(NarrowWindowContext);
  const [curEditState, setCurEditState] = React.useState(editingStates.none); // Working page state
  const [curImageEdit, setCurImageEdit] = React.useState(null);         // The image to edit
  const [curLocationInfo, setCurLocationInfo] = React.useState(null);   // Working location when fetching tooltip
  const [editingLocation, setEditingLocation] = React.useState(true);   // Changing collection locations flag
  const [navigationRedraw, setNavigationRedraw] = React.useState(null); // Forcing redraw on navigation
  const [serverURL, setServerURL] = React.useState(utils.getServer());  // The server URL to use
  const [sidebarWidthLeft, setSidebarWidthLeft] = React.useState(150);  // Width of left sidebar
  const [sidebarHeightTop, setSidebarHeightTop] = React.useState(50);   // Height of top sidebar
  const [sidebarHeightSpecies, setSidebarHeightSpecies] = React.useState(0);   // Height of species sidebar when on top
  const [speciesKeybindName, setSpeciesKeybindName] = React.useState(null); // Name of species for assigning new keybind
  const [speciesRedraw, setSpeciesRedraw] = React.useState(null);       // Force redraw when new species added to image
  const [speciesZoomName, setSpeciesZoomName] = React.useState(null);   // Species to show larger image
  const [workingTop, setWorkingTop] = React.useState(null);             // The absolute top X of workspace
  const [workspaceWidth, setWorkspaceWidth] = React.useState(150);  // The subtracted value is initial sidebar width
  const [totalHeight, setTotalHeight] = React.useState(null);       // Total available height of workspace
  const [tooltipData, setTooltipData] = React.useState(null);       // Data for tooltip
  const [windowSize, setWindowSize] = React.useState({'width':640,'height':480}); // The current window size

  // Some local variables
  const curUploadIdx = sandboxItems.findIndex((item) => item.name == selectedUpload);
  const curUpload = curUploadIdx >= 0 ? sandboxItems[curUploadIdx] : null;
  const curUploadLocation = locationItems.find((item) => item.idProperty == curUpload.location);

  // Bind functions to ensure scope
  const getTooltipInfoOpen = getTooltipInfo.bind(UploadEdit);
  const handleImageSearch = searchImages.bind(UploadEdit);
  const handleEditLocation = editLocation.bind(UploadEdit);
  const handleEditingImage = editingImage.bind(UploadEdit);
  const handleNextImage = nextImage.bind(UploadEdit);
  const handlePrevImage = prevImage.bind(UploadEdit);
  const handleSpeciesChange = speciesChange.bind(UploadEdit);

  let curLocationFetchIdx = -1; // Working index of location data to fetch

  // Render time width and height measurements
  React.useLayoutEffect(() => {
    const newSize = {'width':window.innerWidth,'height':window.innerHeight};
    setWorkspaceWidth(newSize.width - (narrowWindow ? 0 : 150));
    setWindowSize(newSize);
    calcTotalHeight(newSize);
  }, [narrowWindow])

  // Measurements when resizing the window
  React.useLayoutEffect(() => {
      function onResize () {
        let leftWidth = 0;
        let topHeight = 0;
        const newSize = {'width':window.innerWidth,'height':window.innerHeight};

        setWindowSize(newSize);

        calcTotalHeight(newSize);

        // Calculate the top sidebar and add in the species sidebar if it's on top as well
        if (sidebarTopRef && sidebarTopRef.current) {
          topHeight = sidebarTopRef.current.offsetHeight;
          setSidebarHeightTop(topHeight);
        }

        if (sidebarSpeciesRef && sidebarSpeciesRef.current) {
          if (narrowWindow) {
            leftWidth = 0;
            setSidebarWidthLeft(0);
            setSidebarHeightSpecies(sidebarSpeciesRef.current.offsetHeight);
          } else {
            leftWidth = sidebarSpeciesRef.current.offsetWidth;
            setSidebarWidthLeft(leftWidth);
            setSidebarHeightSpecies(0);
          }
        }

        const newWorkspaceWidth = newSize.width - leftWidth;
        setWorkspaceWidth(newWorkspaceWidth);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, [narrowWindow]);

  // Adding drag-and-drop starting attributes to species elements
  React.useLayoutEffect(() => {
    speciesItems.forEach((item) => {
      const el = document.getElementById('card-' + item.name);
      el.addEventListener("dragstart", (ev) => dragstartHandler(ev, item.scientificName));
    });
  }, []);

  // Handling keypress events when adding a species to an image
  React.useEffect(() => {
    function onKeypress(event) {
      if (curEditState == editingStates.editImage) {
        if (event.key !== 'Meta') {
          const speciesKeyItem = speciesItems.find((item) => item.keyBinding == event.key.toUpperCase());
          if (speciesKeyItem) {
            handleSpeciesAdd(speciesKeyItem);
          }
          event.preventDefault();
        }
      }
    }

    document.addEventListener("keydown", onKeypress);

    return () => {
      document.removeEventListener("keydown", onKeypress);
    }
  }, [curEditState,curImageEdit]);

  // Checking if we already have a location for the upload so we skip the initial prompt to assign loc.
  React.useEffect(() => {
    if (curUpload && curUpload.location) {
      onLocationContinue();
    }
  }, [curUpload]);

  /**
   * Common add a species to the current image function
   * @function
   * @param {object} speciesAdd The species to add to the image
   */
  function handleSpeciesAdd(speciesAdd) {
    const haveSpeciesIdx = curImageEdit.species.findIndex((item) => item.name === speciesAdd.name);
    if (haveSpeciesIdx > -1) {
      curImageEdit.species[haveSpeciesIdx].count = parseInt(curImageEdit.species[haveSpeciesIdx].count) + 1;
      window.setTimeout(() => {
        setSpeciesRedraw(curImageEdit.name+curImageEdit.species[haveSpeciesIdx].name+curImageEdit.species[haveSpeciesIdx].count);
      }, 100);
    } else {
      curImageEdit.species.push({name:speciesAdd.name,count:1});
      window.setTimeout(() => {
        setSpeciesRedraw(curImageEdit.name+speciesAdd.name+'1');
      }, 100);
    }
  }

  /**
   * Setting the drag information when drag starts
   * @function
   * @param {object} event The drag start event
   * @param {string} value The drag sequence value
   */
  function dragstartHandler(event, value) {
    // Add the target element's id to the data transfer object
    event.dataTransfer.setData("text/plain", value);
    event.dataTransfer.dropEffect = "copy";
  }

  /**
   * Calculates the total available height for the workspace
   * @function
   * @param {object} curSize The working height and width of the window
   */
  function calcTotalHeight(curSize) {
    const elHeader = document.getElementById('sparcd-header');
    const elFooter = document.getElementById('sparcd-footer');
    const elHeaderSize = elHeader.getBoundingClientRect();
    const elFooterSize = elFooter.getBoundingClientRect();

    let maxHeight = '100px';
    maxHeight = (curSize.height - elHeaderSize.height - elFooterSize.height);

    setTotalHeight(maxHeight);
    setWorkingTop(elHeaderSize.height);

    // Get the top sidebar and add in the species sidebar if it's on top as wel;l
    const elTopSidebar = document.getElementById('top-sidebar');
    if (elTopSidebar) {
      const elTopSidebarSize = elTopSidebar.getBoundingClientRect();
      setSidebarHeightTop(elTopSidebarSize.height);
    } else {
      setSidebarHeightTop(0);
    }

    const elSpeciesSidebar = document.getElementById('species-sidebar');
    if (elSpeciesSidebar) {
      const elSpeciesSidebarSize = elSpeciesSidebar.getBoundingClientRect();
      if (narrowWindow) {
        setSidebarHeightSpecies(elSpeciesSidebarSize.height);
        setSidebarWidthLeft(0);
      } else {
        setSidebarHeightSpecies(0);
        setSidebarWidthLeft(elSpeciesSidebarSize.width);
      }
    }
  }

  /**
   * Updates the server with a new location for the upload
   * @function
   * @param {object} event The current event
   */
  function onLocationContinue(event) {
    const locEl = document.getElementById('upload-edit-location');
    const uploadLocationUrl = serverURL + '/uploadLocation';
    // TODO: save new location on server
    /* TODO: make call and wait for response & return correct result
             need to handle null, 'invalid', and token values
    const resp = await fetch(uploadLocationUrl, {
      'method': 'POST',
      'data': formData
    });
    console.log(resp);
    */
    curUpload.location = locEl.value;
    setCurEditState(editingStates.listImages);
    setEditingLocation(false);
    onSearchSetup('Image Name', handleImageSearch);
  }

  /**
   * Calls the edit cancel function to stop editing an upload
   * @function
   * @param {object} event The current event
   */
  function handleCancel(event) {
    onCancel();
  }

  /**
   * Sets up for changing a species keybinding
   * @function
   * @param {object} event The current event
   * @param {string} name The species name to change
   * @param {object} oldKeybinding The old keybinding value
   */
  function onKeybindClick(event, name, oldKeybinding) {
    setSpeciesZoomName(null);
    if (curEditState !== editingStates.editImage) {
      setSpeciesKeybindName(name);
    } else {
      setSpeciesKeybindName(null);
    }
  }

  /**
   * Updates the server with the changed species keybinding
   * @function
   * @param {string} speciesName The name of the species to change the keybinding for
   * @param {string} newKey The new keybinding character
   */
  function keybindChange(speciesName, newKey) {
    const newKeySpeciesIdx = speciesItems.findIndex((item) => item.name === speciesName);
    if (newKeySpeciesIdx > -1) {
      const keybindUrl = serverURL + '/keybind';
      // TODO: save new keybind on server
      /* TODO: make call and wait for response & return correct result
               need to handle null, 'invalid', and token values
      const resp = await fetch(keybindUrl, {
        'method': 'POST',
        'data': formData
      });
      console.log(resp);
      */
      speciesItems[newKeySpeciesIdx].keyBinding = newKey;
    }
  }

  /**
   * Shows the next image for editing
   * @function
   */
  function nextImage() {
    const curImageIdx =  curUpload.images.findIndex((item) => item.name === curImageEdit.name);
    if (curImageIdx === -1) {
      console.log("Error: unable to find current image before advancing to next image");
      return;
    }
    if (curImageIdx < curUpload.images.length - 1) {
      const newImage = curUpload.images[curImageIdx+1];
      const imageEl = document.getElementById(newImage.name);
      setCurImageEdit(newImage);
      if (imageEl) {
        imageEl.scrollIntoView();
      }
      setNavigationRedraw('redraw-image-'+newImage.name);
    }
  }

  /**
   * Shows the previous image for editing
   * @function
   */
  function prevImage() {
    const curImageIdx =  curUpload.images.findIndex((item) => item.name === curImageEdit.name);
    if (curImageIdx === -1) {
      console.log("Error: unable to find current image before advancing to previous image");
      return;
    }
    if (curImageIdx > 0) {
      const newImage = curUpload.images[curImageIdx-1];
      const imageEl = document.getElementById(newImage.name);
      setCurImageEdit(newImage);
      if (imageEl) {
        imageEl.scrollIntoView();
      }
      setNavigationRedraw('redraw-image-'+newImage.name);
    }
  }

  /**
   * Updates the server when the species count changes
   * @function
   * @param {string} imageName The name of the image getting changed
   * @param {string} speciesName The name of the species whose count is changing
   * @param {int} speciesCount The new count for that species
   */
  function speciesChange(imageName, speciesName, speciesCount) {
    const curImageIdx = curUpload.images.findIndex((item) => item.name === imageName);
    if (curImageIdx === -1) {
      console.log('Warning: Unable to find image for updating species', imageName);
      return;
    }
    const curSpeciesIdx = curUpload.images[curImageIdx].species.findIndex((item) => item.name === speciesName);
    if (curSpeciesIdx === -1) {
      console.log('Warning: Unable to find species',speciesName,'for updating count in image',imageName);
      return;
    }
    curUpload.images[curImageIdx].species[curSpeciesIdx].count = speciesCount;

    const speciesUrl = serverURL + '/uploadSpecies';
    // TODO: save new species count on server
    /* TODO: make call and wait for response & return correct result
             need to handle null, 'invalid', and token values
    const resp = await fetch(speciesUrl, {
      'method': 'POST',
      'data': formData
    });
    console.log(resp);
    */
  }

  /**
   * Calls the server to get location details for tooltips
   * @function
   * @param {int} locIdx The index of the location to get the details for
   */
  function getTooltipInfo(locIdx) {
    if (curLocationFetchIdx != locIdx) {
      curLocationFetchIdx = locIdx;
      const locationUrl = serverURL + '/location';
      /* TODO: make call and wait for response & return correct result
               need to handle null, 'invalid', and token values
      const resp = await fetch(locationUrl, {
        'method': 'POST',
        'data': formData
      });
      console.log(resp);
      */
      // Save the data if we're still fetching the current location
      setTimeout(()  => {
        if (locIdx == curLocationFetchIdx) {
          let locInfo = Object.assign({}, locationItems[curLocationFetchIdx], {'index':locIdx});
          setTooltipData(locInfo);
        }
      }, 100);
    }
  }

  /**
   * Clears tooltip information when no longer needed. Ensures only the working tooltip is cleared
   * @function
   * @param {int} locIdx The index of the location to clear
   */
  function clearTooltipInfo(locIdx) {
    // Only clear the information if we're the active tooltip
    if (locIdx == curLocationFetchIdx) {
      setCurLocationInfo(null);
    }
  }

  /**
   * Searches for images that meet the search criteria and scrolls it into view
   * @function
   * @param {string} searchTerm The term to search an image name for
   */
  function searchImages(searchTerm) {
    const lcSearchTerm = searchTerm.toLowerCase();
    const foundImage = curUpload.images.find((item) => item.name.toLowerCase().includes(lcSearchTerm));
    if (!foundImage) {
      return false;
    }
    const foundEl = document.getElementById(foundImage.name);
    if (!foundEl) {
      return false;
    }

    foundEl.scrollIntoView();
    return true;
  }

  /**
   * Sets the flag indicating the user wants to edit the upload location
   * @function
   */
  function editLocation() {
    setEditingLocation(true);
  }

  /**
   * Called set the page state to a specific image for editing and performs setup functions
   * @function
   * @param {string} imageName The name of the image to edit
   */
  function editingImage(imageName) {
    setCurEditState(editingStates.editImage);
    setCurImageEdit(curUpload.images.find((item) => item.name === imageName));
    onSearchSetup();
  }

  // Calculate the total available height if we don't have anything yet
  if (!totalHeight) {
    calcTotalHeight(windowSize);
  }

  // Variables to help with generating the UI
  const curHeight = totalHeight;
  const curStart = workingTop;
  const workplaceStartX = sidebarWidthLeft;

  /**
   * Generates the image tiles for the available images
   * @function
   * @param {function} clickHandler The handler for when an image tile is clicked
   * @returns {object} The rendered UI
   */
  function generateImageTiles(clickHandler) {
    // TODO: generate only the amount needed to display and override the scroll bar
    return (
      <Grid container rowSpacing={{xs:1, sm:2, md:4}} columnSpacing={{xs:1, sm:2, md:4}}>
      { curUpload.images ? 
        curUpload.images.map((item) => {
          let imageSpecies = item.species && item.species.length > 0;
          return (
            <Grid item size={{ xs: 12, sm: 4, md:3 }} key={item.name}>
              <ImageTile name={item.name} species={item.species} onClick={() => clickHandler(item.name)} />
            </Grid>
          )}
        )
        :
          <Grid item size={{ xs: 12, sm: 12, md:12 }}>
            <Container sx={{border:'1px solid grey', borderRadius:'5px', color:'darkslategrey', background:'#E0F0E0'}}>
              <Typography variant="body" sx={{ color: 'text.secondary' }}>
                No images are available
              </Typography>
            </Container>
          </Grid>
      }
      </Grid>
    );
  }

  // TODO: Make species bar on top when narrow screen
  const topbarVisiblity = curEditState == editingStates.editImage || curEditState == editingStates.listImages ? 'visible' : 'hidden';
  const imageVisibility = (curEditState == editingStates.editImage || curEditState == editingStates.listImages) && !editingLocation ? 'visible' : 'hidden';
  // Return the rendered page
  return (
    <Box id="upload-edit"sx={{ flexGrow: 1, top:curStart+'px', width: '100vw' }} >
      <SpeciesSidebar species={speciesItems}
                      position={narrowWindow?'top':'left'}
                      speciesSidebarRef={sidebarSpeciesRef}
                      workingDim={narrowWindow?'100vw':curHeight+'px'}
                      topX={narrowWindow ? curStart + sidebarHeightTop : curStart} 
                      onKeybind={(event, speciesItem) => {onKeybindClick(event, speciesItem.name, speciesItem.keyBinding);event.preventDefault();}}
                      onZoom={(event, speciesItem) => {setSpeciesZoomName(speciesItem.name);setSpeciesKeybindName(null);event.preventDefault();}}
      />
      <Grid id='top-sidebar' ref={sidebarTopRef} container direction='row' alignItems='center' rows='1' 
          style={{ ...theme.palette.top_sidebar, 'top':curStart+'px', 'minWidth':workspaceWidth+'px', 'maxWidth':workspaceWidth+'px',
                   'position':'sticky', 'left':workplaceStartX, 'verticalAlignment':'middle', 'visibility':topbarVisiblity }} >
        <Grid item>
          <Typography variant="body" sx={{ paddingLeft: '10px'}}>
            {curUpload.name}
          </Typography>
        </Grid>
        <Grid sx={{marginLeft:'auto'}}>
          <Typography variant="body" sx={{ paddingLeft: '10px'}}>
            {curUpload.location}
          </Typography>
          <IconButton aria-label="edit" size="small" color={'lightgrey'} onClick={handleEditLocation}>
            <BorderColorOutlinedIcon sx={{fontSize:'smaller'}}/>
          </IconButton>
        </Grid>
      </Grid>
      { curEditState == editingStates.editImage || curEditState == editingStates.listImages ? 
        <Grid id='image-edit-workspace' container direction="column" alignItems="center" justifyContent="start"
              style={{ 'paddingTop':'10px', 'paddingLeft':'10px',
                       'minHeight':(curHeight-sidebarHeightTop-sidebarHeightSpecies)+'px',
                       'maxHeight':(curHeight-sidebarHeightTop-sidebarHeightSpecies)+'px',
                       'height':(curHeight-sidebarHeightTop-sidebarHeightSpecies)+'px',
                       'top':(curStart+sidebarHeightTop+sidebarHeightSpecies)+'px', 
                       'left':workplaceStartX,
                       'minWidth':workspaceWidth,
                       'maxWidth':workspaceWidth,
                       'width':workspaceWidth, 
                       'position':'absolute', overflow:'scroll', 'visibility':imageVisibility }}>
          <Grid item size={{ xs: 12, sm: 12, md:12 }}>
            {generateImageTiles(handleEditingImage)}
          </Grid>
        </Grid>
        : null
      }
      { curEditState == editingStates.editImage ?
        <Grid id='image-edit-workspace' container direction="column" alignItems="center" justifyContent="center"
              style={{ 'paddingTop':'10px', 'paddingLeft':'10px',
                       'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px',
                       'top':(curStart)+'px', 
                       'left':workplaceStartX, 'minWidth':workspaceWidth, 'maxWidth':workspaceWidth, 'width':workspaceWidth, 
                       'position':'absolute', 'visibility':imageVisibility, backgroundColor:'rgb(0,0,0,0.7)' }}>
          <Grid item size={{ xs: 12, sm: 12, md:12 }}>
            <ImageEdit id={navigationRedraw}
                       url={curImageEdit.url}
                       name={curImageEdit.name}
                       parentX={workplaceStartX} parentId='image-edit-workspace'
                       maxWidth={workspaceWidth-40}
                       maxHeight={curHeight-40} 
                       onClose_func={() => {setCurEditState(editingStates.listImages);onSearchSetup('Image Name', handleImageSearch);}}
                       adjustments={true}
                       dropable={true}
                       navigation={{prev_func:handlePrevImage,next_func:handleNextImage}}
                       species={curImageEdit.species}
                       speciesChange_func={(speciesName, speciesCount) => handleSpeciesChange(curImageEdit.name, speciesName, speciesCount)}
            />
          </Grid>
        </Grid>
        : null
      }
      { editingLocation ? 
          <Grid id='image-edit-workspace' container spacing={0} direction="column" alignItems="center" justifyContent="center"
                style={{ 'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px', 
                        'top':(curStart+sidebarHeightTop)+'px',
                         'left':workplaceStartX+'px','minWidth':workspaceWidth+'px', 'maxWidth':workspaceWidth+'px', 'width':workspaceWidth+'px',
                         'position':'absolute'}}>
              <Grid item size={{ xs: 12, sm: 12, md:12 }}>
                <LocationSelection title={curUpload.name} locations={locationItems} defaultLocation={curUploadLocation} 
                                   onTTOpen={getTooltipInfoOpen} onTTClose={clearTooltipInfo}
                                   dataTT={tooltipData} onContinue={onLocationContinue}
                                   onCancel={curEditState == editingStates.none ? handleCancel : () => setEditingLocation(false)}
                />
            </Grid>
          </Grid>
        : null }
      { speciesZoomName ? 
          <Grid id='image-edit-species-image' container spacing={0} direction="column" alignItems="center" justifyContent="center"
              style={{ 'paddingTop':'10px', 'paddingLeft':'10px',
                       'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px',
                       'top':curStart+'px', 
                       'left':workplaceStartX, 'minWidth':workspaceWidth, 'maxWidth':workspaceWidth, 'width':workspaceWidth, 
                       'position':'absolute', backgroundColor:'rgb(0,0,0,0.7)' }}>
              <Grid item size={{ xs: 12, sm: 12, md:12 }}>
                <ImageEdit url={speciesItems.find((item)=>item.name===speciesZoomName).speciesIconURL} name={speciesZoomName}
                           parentX={workplaceStartX} parentId='image-edit-species-image'
                           maxWidth={workspaceWidth-40} maxHeight={curHeight-40} onClose_func={() => setSpeciesZoomName(null)}
                           adjustments={false}
                />
            </Grid>
          </Grid>
        : null
      }
      { speciesKeybindName && curEditState !== editingStates.editImage ? 
          <Grid id='image-edit-species-keybind' container spacing={0} direction="column" alignItems="center" justifyContent="center"
              style={{ 'paddingTop':'10px', 'paddingLeft':'10px',
                       'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px',
                       'top':curStart+'px', 
                       'left':workplaceStartX, 'minWidth':workspaceWidth, 'maxWidth':workspaceWidth, 'width':workspaceWidth, 
                       'position':'absolute', backgroundColor:'rgb(0,0,0,0.7)' }}>
              <Grid item size={{ xs: 12, sm: 12, md:12 }}>
                <SpeciesKeybind keybind={speciesItems.find((item)=>item.name===speciesKeybindName).keyBinding}
                                name={speciesKeybindName}
                                parentId='image-edit-species-image'
                                onClose_func={() => setSpeciesKeybindName(null)}
                                onChange_func={(newKey) => keybindChange(speciesKeybindName, newKey)}
                />
            </Grid>
          </Grid>
        : null
      }
    </Box>
  );
}
