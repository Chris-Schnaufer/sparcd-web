'use client'

/** @module UploadEdit */

import * as React from 'react';
import BorderColorOutlinedIcon from '@mui/icons-material/BorderColorOutlined';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { LocationsInfoContext, NarrowWindowContext, SizeContext, SpeciesInfoContext, TokenContext, UploadEditContext } from './serverInfo';
import ImageEdit from './ImageEdit';
import ImageTile from './components/ImageTile';
import LocationSelection from './LocationSelection';
import SpeciesKeybind from './components/SpeciesKeybind';
import SpeciesSidebar from './components/SpeciesSidebar';
import SpeciesSidebarItem from './components/SpeciesSidebarItem';
import * as utils from './utils';

/**
 * Handles editing an upload from a collection
 * @function
 * @param {object} selectedUpload The active upload to edit
 * @param {function} onCancel Call when finished with the the upload edit
 * @param {function} searchSetup Call when settting up or clearing search elements
 * @returns {object} The UI to render
 */
export default function UploadEdit({selectedUpload, onCancel, searchSetup}) {
  const theme = useTheme();
  const editingStates = React.useMemo(() => {return({'none':0, 'listImages':2, 'editImage': 3}) }, []); // Different states of this page
  const sidebarSpeciesRef = React.useRef(null);  // Used for sizeing
  const sidebarTopRef = React.useRef(null);   // Used for sizeing
  const curUpload = React.useContext(UploadEditContext);
  const speciesItems = React.useContext(SpeciesInfoContext);
  const locationItems = React.useContext(LocationsInfoContext);
  const narrowWindow = React.useContext(NarrowWindowContext);
  const editToken = React.useContext(TokenContext);  // Login token
  const uiSizes = React.useContext(SizeContext);
  const [curEditState, setCurEditState] = React.useState(editingStates.none); // Working page state
  const [curImageEdit, setCurImageEdit] = React.useState(null);         // The image to edit
  const [curLocationInfo, setCurLocationInfo] = React.useState(null);   // Working location when fetching tooltip
  const [editingLocation, setEditingLocation] = React.useState(true);   // Changing collection locations flag
  const [maxTilesDisplay, setMaxTilesDisplay] = React.useState(40);     // Set the maximum number of tiles to display
  const [navigationRedraw, setNavigationRedraw] = React.useState(null); // Forcing redraw on navigation
  const [observerActive, setObserverActive] = React.useState(false);    // Used to indicate that we've set the observer
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
  const curUploadLocation = locationItems.find((item) => item.idProperty === curUpload.location);

  // Bind functions to ensure scope
  const getTooltipInfoOpen = getTooltipInfo.bind(UploadEdit);
  const handleImageSearch = searchImages.bind(UploadEdit);
  const handleEditLocation = editLocation.bind(UploadEdit);
  const handleEditingImage = editingImage.bind(UploadEdit);
  const handleNextImage = nextImage.bind(UploadEdit);
  const handlePrevImage = prevImage.bind(UploadEdit);
  const handleSpeciesChange = speciesChange.bind(UploadEdit);

  let curLocationFetchIdx = -1; // Working index of location data to fetch
  let workingTileCount = 40;

  /**
   * Calculates the total available height for the workspace
   * @function
   * @param {object} curSize The working height and width of the window
   */
  const calcTotalHeight = React.useCallback((curSize) => {
    setTotalHeight(uiSizes.workspace.height);
    setWorkingTop(uiSizes.workspace.top);

    // Get the top sidebar and add in the species sidebar if it's on top as well
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
  }, [narrowWindow, uiSizes])

  /**
   * Common add a species to the current image function
   * @function
   * @param {object} speciesAdd The species to add to the image
   */
  const handleSpeciesAdd = React.useCallback((speciesAdd) => {
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
  }, [curImageEdit])

  /**
   * Handles the user scrolling past the end of the images, so we load more
   * @function
   */
  const onMoreImages = React.useCallback(() => {
    if (curUpload && curUpload.images && maxTilesDisplay < curUpload.images.length) {
      // Figure out how many tiles across we are
      let rowTilesCount = 4;
      const el = document.getElementById('image-edit-workspace');
      if (el && el.children && el.children.length > 1) {
        const childTop = el.children[0].getBoundingClientRect().top;
        rowTilesCount = 1;
        while (rowTilesCount < 40 && rowTilesCount < curUpload.images.length) {
          if (el.children[rowTilesCount].getBoundingClientRect().top != childTop) {
            break;
          }
          rowTilesCount++;
        }
      }

      workingTileCount = workingTileCount + 40;
      setMaxTilesDisplay(workingTileCount + (workingTileCount % rowTilesCount));
    }
  }, [curUpload, maxTilesDisplay]);

  // Check if we need to setup an interaction observer
  React.useLayoutEffect(() => {
    if (!observerActive) {
      const el = document.getElementById('upload-edit-observer');
      if (el) {
        const observerOptions = {
          root: document.getElementById('image-edit-workspace'),
          rootMargin: "5px",
          threshold: 0.0,
        };
        const observer = new IntersectionObserver(onMoreImages, observerOptions);
        observer.observe(el);
        setObserverActive(observer);
      }
    }
  });

  // Render time width and height measurements
  React.useLayoutEffect(() => {
    setWorkspaceWidth(uiSizes.workspace.width);
    setWindowSize(uiSizes.window);
    calcTotalHeight(uiSizes);
  }, [uiSizes])

  // Measurements when resizing the window
  React.useLayoutEffect(() => {
      function onResize () {
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

        const newWorkspaceWidth = uiSizes.workspace.width - leftWidth;
        setWorkspaceWidth(newWorkspaceWidth);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, [narrowWindow, uiSizes]);

  /**
   * Updates the server with a new location for the upload
   * @function
   * @param {object} event The current event
   */
  const onLocationContinue = React.useCallback((event) => {
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
    searchSetup('Image Name', handleImageSearch);
  }, [curUpload, editingStates.listImages, handleImageSearch, searchSetup, serverURL])

  // Adding drag-and-drop starting attributes to species elements
  React.useLayoutEffect(() => {
    speciesItems.forEach((item) => {
      const el = document.getElementById('card-' + item.name);
      el.addEventListener("dragstart", (ev) => dragstartHandler(ev, item.scientificName));
    });
  }, [speciesItems]);

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
  }, [curEditState,curImageEdit, editingStates, handleSpeciesAdd, speciesItems]);

  // Checking if we already have a location for the upload so we skip the initial prompt to assign loc.
  React.useEffect(() => {
    if (curUpload && curUpload.location) {
      setCurEditState(editingStates.listImages);
      setEditingLocation(false);
      searchSetup('Image Name', handleImageSearch);
    }
  }, [curUpload]);

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

    const speciesUrl = serverURL + '/updateSpecies';
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
      const cur_loc = locationItems[curLocationFetchIdx];
      const locationInfoUrl = serverURL + '/locationInfo?t=' + encodeURIComponent(editToken);

      const formData = new FormData();

      formData.append('id', cur_loc.idProperty);
      formData.append('name', cur_loc.nameProperty);
      formData.append('lat', cur_loc.latProperty);
      formData.append('lon', cur_loc.lngProperty);
      formData.append('ele', cur_loc.elevationProperty);
      try {
        const resp = fetch(locationInfoUrl, {
          credentials: 'include',
          method: 'POST',
          body: formData
        }).then(async (resp) => {
              if (resp.ok) {
                return resp.json();
              } else {
                throw new Error(`Failed to get location information: ${resp.status}`, {cause:resp});
              }
            })
          .then((respData) => {
              // Save tooltip information
              const locInfo = Object.assign({}, respData, {'index':curLocationFetchIdx});

              if (locIdx === curLocationFetchIdx) {
                setTooltipData(locInfo);
              }
                })
          .catch(function(err) {
            console.log('Location tooltip Error: ',err);
        });
      } catch (error) {
        console.log('Location tooltip Unknown Error: ',err);
      }
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
    searchSetup();
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
    const maxTiles = curUpload.images ? Math.min(maxTilesDisplay, curUpload.images.length) : maxTilesDisplay;
    const workingImages = curUpload.images ? curUpload.images.slice(0, maxTiles) : null;
    return (
      <React.Fragment>
      { workingImages ? 
        workingImages.map((item) => {
          let imageSpecies = item.species && item.species.length > 0;
          return (
            <Grid size={{ xs: 12, sm: 4, md:3 }} key={item.name}>
              <ImageTile name={item.name} species={item.species} onClick={() => clickHandler(item.name)} />
            </Grid>
          )}
        )
        :
          <Grid size={{ xs: 12, sm: 12, md:12 }}>
            <Container sx={{border:'1px solid grey', borderRadius:'5px', color:'darkslategrey', background:'#E0F0E0'}}>
              <Typography variant="body" sx={{ color: 'text.secondary' }}>
                No images are available
              </Typography>
            </Container>
          </Grid>
      }
      { workingImages && maxTiles < curUpload.images.length &&
          <Grid id='upload-edit-observer' size={{ xs: 12, sm: 12, md:12 }}>
            <Container sx={{border:0, color:'transparent'}}>
              <div style={{height:'10px', width:'100px'}} />
            </Container>
          </Grid>
      }
      </React.Fragment>
    );
  }

  // TODO: Make species bar on top when narrow screen
  const topbarVisiblity = curEditState == editingStates.editImage || curEditState == editingStates.listImages ? 'visible' : 'hidden';
  const imageVisibility = (curEditState == editingStates.editImage || curEditState == editingStates.listImages) && !editingLocation ? 'visible' : 'hidden';
  // Return the rendered page
  return (
    <Box id="upload-edit"sx={{ flexGrow: 1, top:curStart+'px', height: uiSizes.workspace.height+'px', width: uiSizes.workspace.width+'px' }} >
      <SpeciesSidebar species={speciesItems}
                      position={narrowWindow?'top':'left'}
                      speciesSidebarRef={sidebarSpeciesRef}
                      workingDim={narrowWindow?'100vw':curHeight+'px'}
                      topX={narrowWindow ? curStart + sidebarHeightTop : curStart} 
                      onKeybind={(event, speciesItem) => {onKeybindClick(event, speciesItem.name, speciesItem.keyBinding);event.preventDefault();}}
                      onZoom={(event, speciesItem) => {setSpeciesZoomName(speciesItem.name);setSpeciesKeybindName(null);event.preventDefault();}}
      />
      <Grid id='top-sidebar' ref={sidebarTopRef} container direction='row' alignItems='center' rows='1' 
          style={{ ...theme.palette.top_sidebar, top:curStart+'px', minWidth:(workspaceWidth-workplaceStartX)+'px', maxWidth:(workspaceWidth-workplaceStartX)+'px',
                   position:'sticky', marginLeft:workplaceStartX, verticalAlignment:'middle', visibility:topbarVisiblity }} >
        <Grid>
          <Typography variant="body" sx={{ paddingLeft: '10px'}}>
            {curUpload.name}
          </Typography>
        </Grid>
        <Grid sx={{marginLeft:'auto'}}>
          <Typography variant="body" sx={{ paddingLeft: '10px'}}>
            {curUpload.location && curUpload.location.length ? curUpload.location : '<location>'}
          </Typography>
          <IconButton aria-label="edit" size="small" color={'lightgrey'} onClick={handleEditLocation}>
            <BorderColorOutlinedIcon sx={{fontSize:'smaller'}}/>
          </IconButton>
        </Grid>
      </Grid>
      { curEditState == editingStates.listImages || curEditState == editingStates.editImage ? 
        <Grid id='image-edit-workspace' container direction="row" alignItems="start" justifyContent="start" rowSpacing={{xs:1, sm:2, md:4}} columnSpacing={{xs:1, sm:2, md:4}}
              style={{ 'marginTop':'23px', 'marginLeft':'10px', 'marginRight':'10px',
                       'minHeight':(curHeight-sidebarHeightTop-sidebarHeightSpecies)+'px',
                       'maxHeight':(curHeight-sidebarHeightTop-sidebarHeightSpecies)+'px',
                       'height':(curHeight-sidebarHeightTop-sidebarHeightSpecies)+'px',
                       'top':(curStart+sidebarHeightTop+sidebarHeightSpecies)+'px', 
                       'left':workplaceStartX,
                       'minWidth':(workspaceWidth-sidebarWidthLeft-(10*2))+'px',
                       'maxWidth':(workspaceWidth-sidebarWidthLeft-(10*2))+'px',
                       'width':(workspaceWidth-sidebarWidthLeft-(10*2))+'px', 
                       'position':'absolute', overflow:'scroll', 'visibility':imageVisibility }}>
            {generateImageTiles(handleEditingImage)}
        </Grid>
        : null
      }
      { curEditState == editingStates.editImage ?
        <Grid id='image-edit-edit' container direction="column" alignItems="center" justifyContent="center"
              style={{ 'paddingTop':'10px', 'paddingLeft':'10px',
                       'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px',
                       'top':(curStart)+'px', 
                       'left':workplaceStartX,
                       'minWidth':(workspaceWidth-sidebarWidthLeft)+'px',
                       'maxWidth':(workspaceWidth-sidebarWidthLeft)+'px',
                       'width':(workspaceWidth-sidebarWidthLeft)+'px', 
                       'position':'absolute', 'visibility':imageVisibility, backgroundColor:'rgb(0,0,0,0.7)' }}>
          <Grid >
            <ImageEdit url={curImageEdit.url}
                       name={curImageEdit.name}
                       parentId='image-edit-edit'
                       maxWidth={workspaceWidth-40}
                       maxHeight={curHeight-40} 
                       onClose={() => {setCurEditState(editingStates.listImages);searchSetup('Image Name', handleImageSearch);}}
                       adjustments={true}
                       dropable={true}
                       navigation={{onPrev:handlePrevImage,onNext:handleNextImage}}
                       species={curImageEdit.species}
                       onSpeciesChange={(speciesName, speciesCount) => handleSpeciesChange(curImageEdit.name, speciesName, speciesCount)}
            />
          </Grid>
        </Grid>
        : null
      }
      { editingLocation ? 
          <Grid id='image-edit-location' container spacing={0} direction="column" alignItems="center" justifyContent="center"
                style={{ 'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px', 
                        'top':(curStart+sidebarHeightTop)+'px',
                         'left':workplaceStartX+'px',
                         'minWidth':(workspaceWidth-sidebarWidthLeft)+'px',
                         'maxWidth':(workspaceWidth-sidebarWidthLeft)+'px',
                         'width':(workspaceWidth-sidebarWidthLeft)+'px',
                         'position':'absolute'}}>
            <LocationSelection title={curUpload.name} locations={locationItems} defaultLocation={curUploadLocation} 
                               onTTOpen={getTooltipInfoOpen} onTTClose={clearTooltipInfo}
                               dataTT={tooltipData} onContinue={onLocationContinue}
                               onCancel={curEditState == editingStates.none ? handleCancel : () => setEditingLocation(false)}
            />
          </Grid>
        : null }
      { speciesZoomName ? 
          <Grid id='image-edit-species-image' container spacing={0} direction="column" alignItems="center" justifyContent="center"
              style={{ 'paddingTop':'10px', 'paddingLeft':'10px',
                       'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px',
                       'top':curStart+'px', 
                       'left':workplaceStartX,
                       'minWidth':(workspaceWidth-sidebarWidthLeft)+'px',
                       'maxWidth':(workspaceWidth-sidebarWidthLeft)+'px',
                       'width':(workspaceWidth-sidebarWidthLeft)+'px', 
                       'position':'absolute', backgroundColor:'rgb(0,0,0,0.7)' }}>
              <Grid size={{ xs: 12, sm: 12, md:12 }}>
                <ImageEdit url={speciesItems.find((item)=>item.name===speciesZoomName).speciesIconURL} name={speciesZoomName}
                           parentX={workplaceStartX} parentId='image-edit-species-image'
                           maxWidth={workspaceWidth-40} maxHeight={curHeight-40} onClose={() => setSpeciesZoomName(null)}
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
                       'left':workplaceStartX,
                       'minWidth':(workspaceWidth-sidebarWidthLeft)+'px',
                       'maxWidth':(workspaceWidth-sidebarWidthLeft)+'px',
                       'width':(workspaceWidth-sidebarWidthLeft)+'px', 
                       'position':'absolute', backgroundColor:'rgb(0,0,0,0.7)' }}>
              <Grid size={{ xs: 12, sm: 12, md:12 }}>
                <SpeciesKeybind keybind={speciesItems.find((item)=>item.name===speciesKeybindName).keyBinding}
                                name={speciesKeybindName}
                                parentId='image-edit-species-image'
                                onClose={() => setSpeciesKeybindName(null)}
                                onChange={(newKey) => keybindChange(speciesKeybindName, newKey)}
                />
            </Grid>
          </Grid>
        : null
      }
    </Box>
  );
}
