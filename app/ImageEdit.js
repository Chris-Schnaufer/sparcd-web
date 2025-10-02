'use client'

/** @module ImageEdit */

import * as React from 'react';
import ArrowBackIosOutlinedIcon from '@mui/icons-material/ArrowBackIosOutlined';
import ArrowForwardIosOutlinedIcon from '@mui/icons-material/ArrowForwardIosOutlined';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import HighlightOffOutlinedIcon from '@mui/icons-material/HighlightOffOutlined';
import MuiInput from '@mui/material/Input';
import { styled } from '@mui/material/styles';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import { v4 as uuidv4 } from 'uuid';

import { SpeciesInfoContext, UserSettingsContext } from './serverInfo';
import ImageAdjustments from './components/ImageAdjustments';
import ImageEditSpecies from './components/ImageEditSpecies';
import InputSlider from './components/InputSlider';

// Width of the input field
const Input = styled(MuiInput)`
  width: 42px;
`;

/**
 * Returns the UI for editing an image
 * @function
 * @param {string} url The URL of the image top display
 * @param {string} name The name of the image
 * @param {string} parentId The ID of the parent element to use when positioning
 * @param {int} maxWidth The maximum width of the editing controls
 * @param {int} maxHeight The maximum height of the editing controls
 * @param {function} onClose Called when the user is done editing the image
 * @param {boolean} adjustments Set truthiness to true to allow image adjustments
 * @param {boolean} dropable Set truthiness to true to allow species drag-drop to add to existing species
 * @param {object} navigation Set truthiness to true to display the previous and next navigation elements by providing handlers
 * @param {array} species Array of species already available for the image
 * @param {function} onSpeciesChange Function to call when a species is added or a count is modified
 * @returns {object} The UI to render
 */
export default function ImageEdit({url, name, parentId, maxWidth, maxHeight, onClose, adjustments, dropable,
                                   navigation, species, onSpeciesChange}) {
  const navigationMaskTimeoutId = React.useRef(null);         // Holds the timeout ID for removing the navigation mask
  const speciesItems = React.useContext(SpeciesInfoContext);  // All the species
  const userSettings = React.useContext(UserSettingsContext); // User display settings
  const [brightness, setBrightness] = React.useState(100);    // Image brightness
  const [contrast, setContrast] = React.useState(100);        // Image contrast
  const [hue, setHue] = React.useState(0);    // From 360 to -360
  const [imageSize, setImageSize] = React.useState({width:40,height:40,top:0,left:0,right:40}); // Adjusted when loaded
  const [showAdjustments, setShowAdjustments] = React.useState(false);  // Show image brightness, etc
  const [saturation, setSaturation] = React.useState(100);              // Image saturation
  const [speciesRedraw, setSpeciesRedraw] = React.useState(null);       // Forces redraw due to species change
  const [imageId, setImageId] =  React.useState('image-edit-image-'+uuidv4()); // Unique image ID

  const brightnessRange = {'default':100, 'min':0, 'max':200};
  const contrastRange = {'default':100, 'min':0, 'max':200};
  const hueRange = {'default':0, 'min':-720, 'max':720};
  const saturationRange = {'default':100, 'min':0, 'max':200};

  const NAVIGATION_MASK_TIMEOUT = 500; // The timeout value for showing a navigation mask
  const NAVIGATION_MASK_CLEAR_TIMEOUT = 300; // The timeout value for ensuring the navigation mask is cleared

  // Working species
  let curSpecies = species != undefined ? species : [];

  /**
   * Sets the image size based upon the rendered image
   * @function
   */
  const getImageSize = React.useCallback(() => {
    const el = document.getElementById(imageId);
    if (!el) {
      setImageSize({width:40,height:40,top:0,left:0,right:40});
    } else {
      const elSize = el.getBoundingClientRect();
      setImageSize({'left':elSize.left, 'top':elSize.top, 'width':elSize.width, 'height':elSize.height, 'right':elSize.right });
    }
  }, [imageId, setImageSize])

  // Window resize handler
  React.useLayoutEffect(() => {
      function onResize () {
        getImageSize();
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, [getImageSize]);

  /**
   * Handle when a draggable object is dragged over
   * @function
   * @param {object} event The triggering event
   */
  function dragoverHandler(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
  }

  /**
   * Handles when a species is dropped (as part of drag and drop)
   * @function
   * @param {object} event The triggering event
   */
  function dropHandler(event) {
    event.preventDefault();
    // Get the id of the target and add the moved element to the target's DOM
    const speciesScientificName = event.dataTransfer.getData("text/plain").toUpperCase();
    const speciesKeyItem = speciesItems.find((item) => item.scientificName.toUpperCase() === speciesScientificName);
    if (speciesKeyItem) {
      handleSpeciesAdd(speciesKeyItem);
      if (userSettings.autonext) {
        navigation.onNext();
      }
    }
  }

  /**
   * Common handler for adding a species to the image
   * @function
   * @param {object} speciesAdd The species being added
   */
  function handleSpeciesAdd(speciesAdd) {
    const haveSpeciesIdx = curSpecies.findIndex((item) => item.name === speciesAdd.name);
    if (haveSpeciesIdx > -1) {
      curSpecies[haveSpeciesIdx].count = parseInt(curSpecies[haveSpeciesIdx].count) + 1;
      window.setTimeout(() => {
        setSpeciesRedraw(name+curSpecies[haveSpeciesIdx].name+curSpecies[haveSpeciesIdx].count);
      }, 100);
      onSpeciesChange(speciesAdd.name, curSpecies[haveSpeciesIdx].count);
    } else {
      curSpecies.push({name:speciesAdd.name,scientificName:speciesAdd.scientificName,count:1});
      window.setTimeout(() => {
        setSpeciesRedraw(name+speciesAdd.name+'1');
      }, 100);
      onSpeciesChange(speciesAdd.name, 1);
    }
  }

  /**
   * Called when the user adjusts the brightness value
   * @function
   * @param {int} value The new value
   */
  function adjustBrightness(value) {
    setBrightness((brightnessRange.max-brightnessRange.min) * (value / 100.0));
  }

  /**
   * Called when the user adjusts the contrast value
   * @function
   * @param {int} value The new value
   */
  function adjustContrast(value) {
    setContrast((contrastRange.max-contrastRange.min) * (value / 100.0));
  }

  /**
   * Called when the user adjusts the hue value
   * @function
   * @param {int} value The new value
   */
  function adjustHue(value) {
    const newValue = value < 50 ? (hueRange.min * (1.0 - (value / 50.0))) : (hueRange.max * ((value - 50.0) / 50.0));
    setHue(newValue);
  }

  /**
   * Called when the user adjusts the saturation value
   * @function
   * @param {int} value The new value
   */
  function adjustSaturation(value) {
    setSaturation((saturationRange.max-saturationRange.min) * (value / 100.0));
  }

  /**
   * Handles the user changing the count for a species
   * @function
   * @param {object} event The triggering event
   * @param {string} speciesName The name of the species whose count is changing
   */
  const handleInputChange = React.useCallback((event, speciesName) => {
    const newValue = event.target.value === '' ? 0 : Number(event.target.value);
    let workingSpecies = curSpecies;
    const speciesIdx = workingSpecies.findIndex((item) => item.name === speciesName);
    if (speciesIdx == -1) {
      console.log('Error: unable to find species for updating count', speciesName);
      return;
    }

    // Do nothing if the value hasn't changed
    if (workingSpecies[speciesIdx].count == newValue) {
      return;
    }

    // Make the change
    onSpeciesChange(speciesName, newValue);
    workingSpecies[speciesIdx].count = newValue;
    curSpecies = workingSpecies;
    setSpeciesRedraw(workingSpecies[speciesIdx].name+workingSpecies[speciesIdx].count);
  }, [curSpecies, onSpeciesChange, setSpeciesRedraw]);

  /**
   * Handler for when a species input field no longer has focus
   * @function
   * @param {object} event The triggering event
   * @param {string} speciesName The name of the species associated with the event
   */
  const handleBlur = React.useCallback((event, speciesName) => {
    let workingSpecies = curSpecies;
    const speciesIdx = workingSpecies.findIndex((item) => item.name === speciesName);
    if (speciesIdx == -1) {
      console.log('Error: unable to find species for final checks', speciesName);
      return;
    }
    let newValue = workingSpecies[speciesIdx].count;
    if (newValue < 0) {
      newValue = 0;
    } else if (newValue > 100) {
      newValue = 100;
    }
    onSpeciesChange(speciesName, newValue);
    workingSpecies[speciesIdx].count = newValue;
    curSpecies = workingSpecies;
    setSpeciesRedraw(workingSpecies[speciesIdx].name+workingSpecies[speciesIdx].count);
  }, [curSpecies, onSpeciesChange, setSpeciesRedraw]);

  /**
   * Handles deleting a species from the image
   * @function
   * @param {string} speciesName The name of the species to delete
   */
  function handleSpeciesDelete(speciesName) {
    let workingSpecies = curSpecies;
    const speciesIdx = workingSpecies.findIndex((item) => item.name === speciesName);
    if (speciesIdx == -1) {
      console.log('Error: unable to find species for deletion', speciesName);
      return;
    }
    const removedSpecies = workingSpecies[speciesIdx];
    onSpeciesChange(speciesName, 0);
    workingSpecies.splice(speciesIdx, 1);
    curSpecies = workingSpecies;
    setSpeciesRedraw(removedSpecies.name+'-deleted');
  }

  /**
   * Shows the navigation mask
   * @function
   */
  function showNavigationMask() {
    // Show the mask
    const el = document.getElementById("image-edit-navigate-mask");
    if (el) {
      el.style.display = "initial";
      el.style.visibility = "visible";
    }
  }

  /**
   * Hides the navigation mask
   * @function
   */
  function hideNavigationMask() {
    // Hide the mask
    const el = document.getElementById("image-edit-navigate-mask");
    if (el) {
      el.style.display = "none";
      el.style.visibility = "hidden";
    }
  }

  /**
   * Handles the click of the prev image button
   * @function
   */
  const handleNavigationPrev = React.useCallback(() => {
    // Check if we have a pending timeout and cancel it
    const curNavMaskTimeoutId = navigationMaskTimeoutId.current;
    if (curNavMaskTimeoutId) {
      navigationMaskTimeoutId.current = null;
      window.clearTimeout(curNavMaskTimeoutId);
    }

    // Show the mask after a timeout
    navigationMaskTimeoutId.current = window.setTimeout(() => {
          // Clear our timer ID and show the mask
          navigationMaskTimeoutId.current = null;
          showNavigationMask();
      }, NAVIGATION_MASK_TIMEOUT);

    // Perform the navigation
    navigation.onPrev()
  }, [navigation]);

  /**
   * Handles the click of the next image button
   * @function
   */
  const handleNavigationNext = React.useCallback(() => {
    // Check if we have a pending timeout and cancel it
    const curNavMaskTimeoutId = navigationMaskTimeoutId.current;
    if (curNavMaskTimeoutId) {
      navigationMaskTimeoutId.current = null;
      window.clearTimeout(curNavMaskTimeoutId);
    }

    // Show the mask after a timeout
    navigationMaskTimeoutId.current = window.setTimeout(() => {
          // Clear our timer ID and show the mask
          navigationMaskTimeoutId.current = null;
          showNavigationMask();
      }, NAVIGATION_MASK_TIMEOUT);

    // Perform the navigation
    navigation.onNext();
  }, [navigation]);

  /**
   * Handles when the image loads
   * @function
   */
  const onImageLoad = React.useCallback(() => {
    // Hide the navigation mask
    const curNavMaskTimeoutId = navigationMaskTimeoutId.current;
    if (curNavMaskTimeoutId) {
      navigationMaskTimeoutId.current = null;
      window.clearTimeout(curNavMaskTimeoutId);

      // Clear the mask and set a timer to ensure the mask is cleared in case there's timeout overlaps
      hideNavigationMask();
      window.setTimeout(() => hideNavigationMask(), NAVIGATION_MASK_CLEAR_TIMEOUT);
    } else {
      hideNavigationMask();
    }

    // Get the image dimensions    
    getImageSize();
  }, [getImageSize]);

  // Return the rendered UI
  const rowHeight = imageSize.height / 3.0; // Use for the overlays on the image
  const dropExtras = dropable ? {onDrop:dropHandler,onDragOver:dragoverHandler} : {};
  return (
    <React.Fragment>
      <Box id="edit-image-frame" sx={{backgroundColor:'white', padding:'10px 8px', position:'relative'}} {...dropExtras} >
        <img id={imageId} src={url} alt={name} onLoad={onImageLoad}
             style={{maxWidth:maxWidth, maxHeight:maxHeight, 
                     filter:'brightness('+brightness+'%) contrast('+contrast+'%) hue-rotate(' + hue + 'deg) saturate(' + saturation + '%)'}} 
        />
        <Stack style={{ position:'absolute', top:(10)+'px', left:10+'px', minWidth:imageSize.width+'px',
                       maxWidth:imageSize.width+'px', width:imageSize.width+'px', minHeight:maxHeight, maxHeight:maxHeight, 
                    }}
        >
          <Grid container direction="row" alignItems="start" justifyContent="start" sx={{minHeight:rowHeight,maxHeight:rowHeight}}>
            <Grid size={{ xs: 4, sm: 4, md:4 }} sx={{position:'relative'}}>
              <ImageAdjustments isVisible={!!adjustments} onBrightnessChange={adjustBrightness} 
                                onContrastChange={adjustContrast} onHueChange={adjustHue} onSaturationChange={adjustSaturation} />
            </Grid>
            <Grid container alignItems="center" justifyContent="center" size={{ xs: 4, sm: 4, md:4 }} sx={{marginLeft:'auto', cursor:'default'}}>
              <Typography variant="body" sx={{textTransform:'uppercase',color:'grey',textShadow:'1px 1px black','&:hover':{color:'white'} }}>
                {name}
              </Typography>
            </Grid>
            <Grid container alignItems="right" justifyContent="right" size={{ xs: 4, sm: 4, md:4 }} style={{marginLeft:'auto', cursor:'default'}}>
              <div id="image-edit-close" sx={{height:'20px', flex:'1'}} onClick={() => onClose()}>
                <Typography variant="body3" sx={{textTransform:'uppercase',color:'black',backgroundColor:'rgba(255,255,255,0.3)',
                                                 padding:'3px 3px 3px 3px',borderRadius:'3px','&:hover':{backgroundColor:'rgba(255,255,255,0.7)'}
                                               }}>
                  X
                </Typography>
              </div>
            </Grid>
          </Grid>
          { navigation ?
            <Grid container direction="row" alignItems="center" justifyContent="center" sx={{minHeight:rowHeight,maxHeight:rowHeight}}>
              <Grid size="grow" sx={{position:'relative', marginRight:'auto'}}>
                <ArrowBackIosOutlinedIcon fontSize="large" onClick={handleNavigationPrev}
                          sx={{backgroundColor:'rgba(255,255,255,0.3)', '&:hover':{backgroundColor:'rgba(255,255,255,0.7)'} }} />
              </Grid>
              <Grid container alignItems="right" justifyContent="right" size={{ xs: 6, sm: 6, md:6 }} sx={{position:'relative', marginLeft:'auto'}}>
                <ArrowForwardIosOutlinedIcon fontSize="large" onClick={handleNavigationNext}
                          sx={{backgroundColor:'rgba(255,255,255,0.3)', '&:hover':{backgroundColor:'rgba(255,255,255,0.7)'} }} />
              </Grid>
            </Grid>
            : null
          }
          <Grid container id="image-edit-species" direction="row" alignItems="end" justifyContent="end"
                sx={{minHeight:rowHeight,maxHeight:rowHeight}}
          >
            <Grid size={{ xs:6, sm:6, md:6 }} sx={{position:'relative', marginRight:'auto',
                  visibility:(curSpecies ? 'visible' : 'hidden')}}>
              {curSpecies.map((curItem) =>
                <ImageEditSpecies key={name+curItem.name} name={curItem.name?curItem.name:curItem.scientificName} count={curItem.count} onDelete={handleSpeciesDelete}
                                  onChange={handleInputChange} onBlur={handleBlur} />
              )}
            </Grid>
          </Grid>
          { navigation &&
            <Box id="image-edit-navigate-mask" sx={{position:"absolute", left:"0px", top:"0px", minWidth:imageSize.width, minHeight:imageSize.height,
                    backgroundColor:"rgb(255, 255, 255, 0.8)", display:"none"}} />
          }
        </Stack>
      </Box>
    </React.Fragment>
  );
}