'use client'

import * as React from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import BorderColorOutlinedIcon from '@mui/icons-material/BorderColorOutlined';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActionArea from '@mui/material/CardActionArea';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import CheckCircleOutlinedIcon from '@mui/icons-material/CheckCircleOutlined';
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Fade from '@mui/material/Fade';
import FormControl from '@mui/material/FormControl';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import ImageOutlinedIcon from '@mui/icons-material/ImageOutlined';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { LocationsInfoContext, SandboxInfoContext, SpeciesInfoContext } from './serverInfo'
import ImageEdit from './components/ImageEdit'
import SpeciesKeybind from './components/SpeciesKeybind'
import SpeciesSidebarItem from './components/SpeciesSidebarItem'
import * as utils from './utils'

export default function UploadEdit({selectedUpload, onCancel_func, searchSetup_func}) {
  const theme = useTheme();
  const editingStates = {'none':0, 'listImages':2, 'editImage': 3};
  const sidebarLeftRef = React.useRef();
  const sidebarTopRef = React.useRef();
  const sandboxItems = React.useContext(SandboxInfoContext);
  const speciesItems = React.useContext(SpeciesInfoContext);
  const locationItems = React.useContext(LocationsInfoContext);
  const [curEditState, setCurEditState] = React.useState(editingStates.none);
  const [curImageEdit, setCurImageEdit] = React.useState(null);
  const [curLocationInfo, setCurLocationInfo] = React.useState(null);
  const [editingLocation, setEditingLocation] = React.useState(true);
  const [navigationRedraw, setNavigationRedraw] = React.useState(null);
  const [serverURL, setServerURL] = React.useState(utils.getServer());
  const [sidebarWidthLeft, setSidebarWidthLeft] = React.useState(150);
  const [sidebarHeightTop, setSidebarHeightTop] = React.useState(50);
  const [speciesKeybindName, setSpeciesKeybindName] = React.useState(null);
  const [speciesRedraw, setSpeciesRedraw] = React.useState(null);
  const [speciesZoomName, setSpeciesZoomName] = React.useState(null);
  const [workingTop, setWorkingTop] = React.useState(null);
  const [workspaceWidth, setWorkspaceWidth] = React.useState(150); // The subtracted value is initial sidebar width
  const [totalHeight, setTotalHeight] = React.useState(null);
  const [tooltipData, setTooltipData] = React.useState(null);
  const [windowSize, setWindowSize] = React.useState({'width':640,'height':480});

  const curUploadIdx = sandboxItems.findIndex((item) => item.name == selectedUpload);
  const curUpload = curUploadIdx >= 0 ? sandboxItems[curUploadIdx] : null;
  const curUploadLocation = locationItems.find((item) => item.idProperty == curUpload.location);
  const getTooltipInfoOpen = getTooltipInfo.bind(UploadEdit);
  const handleImageSearch = searchImages.bind(UploadEdit);
  const handleEditLocation = editLocation.bind(UploadEdit);
  const handleEditingImage = editingImage.bind(UploadEdit);
  const handleNextImage = nextImage.bind(UploadEdit);
  const handlePrevImage = prevImage.bind(UploadEdit);
  const handleSpeciesChange = speciesChange.bind(UploadEdit);
  let curLocationFetchIdx = -1;


  React.useLayoutEffect(() => {
    const newSize = {'width':window.innerWidth,'height':window.innerHeight};
    setWorkspaceWidth(newSize.width - 150);
    setWindowSize(newSize);
    calcTotalHeight(newSize);
  }, [])

  React.useLayoutEffect(() => {
      function onResize () {
        let leftWidth = 0;
        let topHeight = 0;
        const newSize = {'width':window.innerWidth,'height':window.innerHeight};

        setWindowSize(newSize);

        calcTotalHeight(newSize);

        if (sidebarLeftRef && sidebarLeftRef.current) {
          leftWidth = sidebarLeftRef.current.offsetWidth;
          setSidebarWidthLeft(leftWidth);
        }
        if (sidebarTopRef && sidebarTopRef.current) {
          topHeight = sidebarTopRef.current.offsetHeight;
          setSidebarHeightTop(topHeight);
        }

        const newWorkspaceWidth = newSize.width - leftWidth;
        setWorkspaceWidth(newWorkspaceWidth);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  React.useLayoutEffect(() => {
    speciesItems.forEach((item) => {
      const el = document.getElementById('card-' + item.name);
      el.addEventListener("dragstart", (ev) => dragstartHandler(ev, item.scientificName));
    });
  }, []);

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

  React.useEffect(() => {
    if (curUpload && curUpload.location) {
      onContinue();
    }
  }, [curUpload]);

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

  function dragstartHandler(ev, value) {
    // Add the target element's id to the data transfer object
    ev.dataTransfer.setData("text/plain", value);
    ev.dataTransfer.dropEffect = "copy";
  }

  function calcTotalHeight(curSize) {
    const elHeader = document.getElementById('sparcd-header');
    const elFooter = document.getElementById('sparcd-footer');
    const elHeaderSize = elHeader.getBoundingClientRect();
    const elFooterSize = elFooter.getBoundingClientRect();

    let maxHeight = '100px';
    maxHeight = (curSize.height - elHeaderSize.height - elFooterSize.height);

    setTotalHeight(maxHeight);
    setWorkingTop(elHeaderSize.height);

    const elLeftSidebar = document.getElementById('left-sidebar');
    if (elLeftSidebar) {
      const elLeftSidebarSize = elLeftSidebar.getBoundingClientRect();
      setSidebarWidthLeft(elLeftSidebarSize.width);
    }

    const elTopSidebar = document.getElementById('top-sidebar');
    if (elTopSidebar) {
      const elTopSidebarSize = elTopSidebar.getBoundingClientRect();
      setSidebarHeightTop(elTopSidebarSize.height);
    } else {
      setSidebarHeightTop(0);
    }
  }

  function onContinue(ev) {
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
    console.log('Continue:',locEl.value);
    curUpload.location = locEl.value;
    setCurEditState(editingStates.listImages);
    setEditingLocation(false);
    searchSetup_func('Image Name', handleImageSearch);
  }

  function onCancel(ev) {
    onCancel_func();
  }

  function onKeybindClick(ev, name, oldKeybinding) {
    setSpeciesZoomName(null);
    if (curEditState !== editingStates.editImage) {
      setSpeciesKeybindName(name);
    } else {
      setSpeciesKeybindName(null);
    }
  }

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

  function clearTooltipInfo(locIdx) {
    // Only clear the information if we're the active tooltip
    if (locIdx == curLocationFetchIdx) {
      setCurLocationInfo(null);
    }
  }

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

  function editLocation() {
    setEditingLocation(true);
  }

  function editingImage(item, imageName) {
    setCurEditState(editingStates.editImage);
    setCurImageEdit(curUpload.images.find((item) => item.name === imageName));
    searchSetup_func();
  }

  if (!totalHeight) {
    calcTotalHeight(windowSize);
  }

  const curHeight = totalHeight;
  const curStart = workingTop;
  const workplaceStartX = sidebarWidthLeft;

  function generateImageSvg(bgColor, fgColor) {
    if (bgColor == null) {
      bgColor = 'lightgrey';
    }
    if (fgColor == null) {
      fgColor = '#959595';
    }
    return (
      <svg
          viewBox="0 0 150 150"
          xmlns="http://www.w3.org/2000/svg"
          stroke="black"
          fill="grey"
          height="50px"
          width="50px">
        <circle cx='40%' cy='15%' r='2' fill={fgColor} stroke='transparent' strokeWidth='0px' />
        <rect x='10%' y='10%' width='80%' height='80%' fill={bgColor} opacity='0.75' stroke='transparent' strokeWidth='0px'/>
        <line x1='15%' y1='15%' x2='40%' y2='15%' stroke={fgColor} strokeWidth={6}/>
        <circle cx='15%' cy='15%' r='3' fill={fgColor} stroke='transparent' strokeWidth='0px' />
        <line x1='15%' y1='15%' x2='15%' y2='85%' stroke={fgColor} strokeWidth={6}/>
        <circle cx='15%' cy='85%' r='3' fill={fgColor} stroke='transparent' strokeWidth='0px' />
        <line x1='15%' y1='85%' x2='85%' y2='85%' stroke={fgColor} strokeWidth={6}/>
        <circle cx='85%' cy='85%' r='3' fill={fgColor} stroke='transparent' strokeWidth='0px' />
        <line x1='85%' y1='15%' x2='85%' y2='85%' stroke={fgColor} strokeWidth={6}/>
        <circle cx='85%' cy='15%' r='3' fill={fgColor} stroke='transparent' strokeWidth='0px' />
        <line x1='60%' y1='15%' x2='85%' y2='15%' stroke={fgColor} strokeWidth={6}/>
        <circle cx='60%' cy='15%' r='3' fill={fgColor} stroke='transparent' strokeWidth='0px' />
        <path d="M 90 60 L 60 60 L 53 65 L 53 75 L 59 75 L 65 70 L 67 76 L 66 87 L 63 87 L 63 89 L 69 89 L 77 75 L 80 77 L 82 78 L 83 88 L 79 88 L 86 88 L 86 80 L 92 81 L 95 88 L 92 88 L 92 89 L 100 89 L 100 69 L 90 60"
              fill={fgColor} stroke={fgColor} strokeWidth='3px' />
      </svg>
    );
  }

  function generateEditingLocation(continueFunc, cancelFunc) {
    return (
      <Card id='change-location' variant='outlined' sx={{...theme.palette.upload_edit_locations_card}}>
        <CardContent>
          <Typography variant="h5" sx={{ color:'text.primary', textAlign:'center' }}>
            {curUpload.name}
          </Typography>
          <FormControl fullWidth>
            <Autocomplete
              options={locationItems}
              id="upload-edit-location"
              autoHighlight
              defaultValue={curUploadLocation}
              getOptionLabel={(option) => option.idProperty}
              getOptionKey={(option) => option.idProperty+option.latProperty+option.lngProperty}
              onChange={() => console.log('CHANGE')}
              renderOption={(props, loc) => {
                const { key, ...optionProps } = props;
                return (<MenuItem id={loc.idProperty+'-'+key} value={loc.idProperty} key={key} {...optionProps}>
                          <Grid container>
                            <Grid item sm={6} md={6} lg={6}>
                              <Box display="flex" justifyContent="flex-start">
                                {loc.idProperty}
                              </Box>
                            </Grid>
                          <Grid item sm={6} md={6} lg={6} zeroMinWidth>
                            <Box display="flex" justifyContent="flex-end">
                              <Typography variant="body" sx={{ fontSize:'small', overflow:"clip"}}>
                                {loc.nameProperty}
                              </Typography>
                              &nbsp;
                              <Tooltip
                                onOpen={() => getTooltipInfoOpen(props["data-option-index"])}
                                onClose={() => clearTooltipInfo(props["data-option-index"])}
                                title={
                                  tooltipData && tooltipData.index==props["data-option-index"] ?
                                    <React.Fragment>
                                      <Typography color={theme.palette.text.primary} sx={{fontSize:'small'}}>{loc.idProperty}</Typography>
                                      <Typography color={theme.palette.text.primary} sx={{fontSize:'x-small'}}>{loc.latProperty + ", " + loc.lngProperty}</Typography>
                                      <Typography color={theme.palette.text.primary} sx={{fontSize:'x-small'}}>{'Elevation: '+loc.elevationProperty}</Typography>
                                    </React.Fragment>
                                    : 
                                    <React.Fragment>
                                      <Typography color={theme.palette.text.secondary} sx={{fontSize:'small'}}>{loc.idProperty}</Typography>
                                      <Typography color={theme.palette.text.secondary} sx={{fontSize:'x-small'}}>{"------, ------"}</Typography>
                                      <Typography color={theme.palette.text.secondary} sx={{fontSize:'x-small'}}>{'Elevation: ----'}</Typography>
                                      <div style={{...theme.palette.upload_edit_locations_spinner_background}}>
                                      <CircularProgress size={40} sx={{position:'absolute', left:'17px', top:'12px'}}/>
                                      </div>
                                    </React.Fragment>
                                }
                              >
                              <InfoOutlinedIcon color="info" fontSize="small" id="InfoOutlinedIcon"/>
                              </Tooltip>
                            </Box>
                            </Grid>
                          </Grid>
                        </MenuItem> 
                );
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
          <Button sx={{'flex':'1'}} size="small" onClick={continueFunc} >Continue</Button>
          <Button sx={{'flex':'1'}} size="small" onClick={cancelFunc} >Cancel</Button>
        </CardActions>
      </Card>
    );
  }

  function generateImageTiles(clickHandler) {
    return (
      <Grid container rowSpacing={{xs:1, sm:2, md:4}} columnSpacing={{xs:1, sm:2, md:4}}>
      { curUpload.images ? 
        curUpload.images.map((item) => {
          let imageSpecies = item.species && item.species.length > 0;
          return (
            <Grid item size={{ xs: 12, sm: 4, md:3 }} key={item.name}>
              <Card id={item.name} onClick={() => clickHandler(item, item.name)} variant={imageSpecies?"soft":"outlined"}
                    sx={{minWidth:'200px', '&:hover':{backgroundColor:theme.palette.action.active} }}>
                <CardActionArea data-active={imageSpecies ? '' : undefined}
                  sx={{height: '100%', '&[data-active]': {backgroundColor:theme.palette.action.active} }}
                >
                  <CardContent>
                    <Grid container spacing={1}>
                      <Grid item>
                        {generateImageSvg(imageSpecies ? 'grey':null, imageSpecies ? '#68AB68':null)}
                      </Grid>
                      <Grid item>
                        <Box>
                          <Typography variant="body" sx={{textTransform:'uppercase'}}>
                            {item.name}
                            {imageSpecies ? <CheckCircleOutlinedIcon size="small" sx={{color:"#68AB68"}}/> : null}
                          </Typography>
                        </Box>
                          { imageSpecies ?
                            item.species.map((curSpecies,idxSpecies) => 
                                  <Box key={item.name+curSpecies.name+idxSpecies} >
                                    <Typography variant="body3" sx={{textTransform:'capitalize'}}>
                                      {curSpecies.name + ': ' + curSpecies.count}
                                    </Typography>
                                  </Box>
                            )
                            : null
                          }
                      </Grid>
                    </Grid>
                  </CardContent>
                </CardActionArea>
              </Card>
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
  return (
    <Box id="upload-edit"sx={{ flexGrow: 1, top:curStart+'px', width: '100vw' }} >
      <Grid id='left-sidebar' ref={sidebarLeftRef} container direction='row' alignItems='stretch' columns='1' 
          style={{ 'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px', 'top':curStart+'px', 
                   'position':'absolute', 'overflow':'scroll', ...theme.palette.species_left_sidebar }} >
        { speciesItems.map((item, idx) => <SpeciesSidebarItem id={'card-' + item.name} species={item} key={item.name}
                                                             keybindClick_func={(ev) => {onKeybindClick(ev, item.name, item.keyBinding);;ev.preventDefault();}}
                                                             zoomClick_func={(ev) => {setSpeciesZoomName(item.name);setSpeciesKeybindName(null);ev.preventDefault();}}
                                                             />) }
      </Grid>
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
                       'minHeight':(curHeight-sidebarHeightTop)+'px', 'maxHeight':(curHeight-sidebarHeightTop)+'px', 'height':(curHeight-sidebarHeightTop)+'px',
                       'top':curStart+sidebarHeightTop+'px', 
                       'left':workplaceStartX, 'minWidth':workspaceWidth, 'maxWidth':workspaceWidth, 'width':workspaceWidth, 
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
                       'top':curStart+'px', 
                       'left':workplaceStartX, 'minWidth':workspaceWidth, 'maxWidth':workspaceWidth, 'width':workspaceWidth, 
                       'position':'absolute', 'visibility':imageVisibility, backgroundColor:'rgb(0,0,0,0.7)' }}>
          <Grid item size={{ xs: 12, sm: 12, md:12 }}>
            <ImageEdit id={navigationRedraw}
                       url={curImageEdit.url}
                       name={curImageEdit.name}
                       parentX={workplaceStartX} parentId='image-edit-workspace'
                       maxWidth={workspaceWidth-40}
                       maxHeight={curHeight-40} 
                       onClose_func={() => {setCurEditState(editingStates.listImages);searchSetup_func('Image Name', handleImageSearch);}}
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
                style={{ 'minHeight':curHeight+'px', 'maxHeight':curHeight+'px', 'height':curHeight+'px', 'top':curStart+sidebarHeightTop+'px',
                         'left':workplaceStartX+'px','minWidth':workspaceWidth+'px', 'maxWidth':workspaceWidth+'px', 'width':workspaceWidth+'px',
                         'position':'absolute'}}>
              <Grid item size={{ xs: 12, sm: 12, md:12 }}>
                {generateEditingLocation(onContinue, curEditState == editingStates.none ? onCancel : () => setEditingLocation(false))}
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
