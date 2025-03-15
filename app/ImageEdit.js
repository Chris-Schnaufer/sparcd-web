'use client'

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

import { SpeciesInfoContext } from './serverInfo'
import ImageAdjustments from './components/ImageAdjustments'
import ImageEditSpecies from './components/ImageEditSpecies'
import InputSlider from './components/InputSlider'

// Width of the input field
const Input = styled(MuiInput)`
  width: 42px;
`;

export default function ImageEdit({url, name, parentId, maxWidth, maxHeight, onClose_func, adjustments, dropable,
                                   navigation, species, speciesChange_func}) {
  const speciesItems = React.useContext(SpeciesInfoContext);
  const [brightness, setBrightness] = React.useState(100);
  const [contrast, setContrast] = React.useState(100);
  const [hue, setHue] = React.useState(0);    // From 360 to -360
  const [imageSize, setImageSize] = React.useState({width:40,height:40,top:0,left:0,right:40});
  const [showAdjustments, setShowAdjustments] = React.useState(false);
  const [saturation, setSaturation] = React.useState(100);
  const [speciesRedraw, setSpeciesRedraw] = React.useState(null);
  const [imageId, setImageId] =  React.useState('image-edit-image-'+Math.random());
  const brightnessRange = {'default':100, 'min':0, 'max':200};
  const contrastRange = {'default':100, 'min':0, 'max':200};
  const hueRange = {'default':0, 'min':-720, 'max':720};
  const saturationRange = {'default':100, 'min':0, 'max':200};

  let curSpecies = species != undefined ? species : [];

  getImageSize = getImageSize.bind(ImageEdit);
  handleInputChange = handleInputChange.bind(ImageEdit);
  handleBlur = handleBlur.bind(ImageEdit);

  React.useLayoutEffect(() => {
      function onResize () {
        getImageSize();
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  function dragoverHandler(ev) {
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "copy";
  }

  function dropHandler(ev) {
    ev.preventDefault();
    // Get the id of the target and add the moved element to the target's DOM
    const speciesScientificName = ev.dataTransfer.getData("text/plain").toUpperCase();
    const speciesKeyItem = speciesItems.find((item) => item.scientificName.toUpperCase() === speciesScientificName);
    if (speciesKeyItem) {
      handleSpeciesAdd(speciesKeyItem);
    }
  }

  function handleSpeciesAdd(speciesAdd) {
    const haveSpeciesIdx = curSpecies.findIndex((item) => item.name === speciesAdd.name);
    if (haveSpeciesIdx > -1) {
      curSpecies[haveSpeciesIdx].count = parseInt(curSpecies[haveSpeciesIdx].count) + 1;
      window.setTimeout(() => {
        setSpeciesRedraw(name+curSpecies[haveSpeciesIdx].name+curSpecies[haveSpeciesIdx].count);
      }, 100);
    } else {
      curSpecies.push({name:speciesAdd.name,count:1});
      window.setTimeout(() => {
        setSpeciesRedraw(name+speciesAdd.name+'1');
      }, 100);
    }
  }

  function adjustBrightness(value) {
    setBrightness((brightnessRange.max-brightnessRange.min) * (value / 100.0));
  }

  function adjustContrast(value) {
    setContrast((contrastRange.max-contrastRange.min) * (value / 100.0));
  }

  function adjustHue(value) {
    const newValue = value < 50 ? (hueRange.min * (1.0 - (value / 50.0))) : (hueRange.max * ((value - 50.0) / 50.0));
    setHue(newValue);
  }

  function adjustSaturation(value) {
    setSaturation((saturationRange.max-saturationRange.min) * (value / 100.0));
  }

  function getImageSize() {
    const el = document.getElementById(imageId);
    if (!el) {
      setImageSize({width:40,height:40,top:0,left:0,right:40});
    } else {
      const elSize = el.getBoundingClientRect();
      setImageSize({'left':elSize.left, 'top':elSize.top, 'width':elSize.width, 'height':elSize.height, 'right':elSize.right });
    }
  }

  function handleInputChange(event, speciesName) {
    const newValue = event.target.value === '' ? 0 : Number(event.target.value);
    speciesChange_func(speciesName, newValue);
    let workingSpecies = curSpecies;
    const speciesIdx = workingSpecies.findIndex((item) => item.name === speciesName);
    if (speciesIdx == -1) {
      console.log('Error: unable to find species for updating count', speciesName);
      return;
    }
    workingSpecies[speciesIdx].count = newValue;
    curSpecies = workingSpecies;
    setSpeciesRedraw(workingSpecies[speciesIdx].name+workingSpecies[speciesIdx].count);
  };

  function handleBlur(event, speciesName) {
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
    speciesChange_func(speciesName, newValue);
    workingSpecies[speciesIdx].count = newValue;
    curSpecies = workingSpecies;
    setSpeciesRedraw(workingSpecies[speciesIdx].name+workingSpecies[speciesIdx].count);
  }

  function handleSpeciesDelete(speciesName) {
    let workingSpecies = curSpecies;
    const speciesIdx = workingSpecies.findIndex((item) => item.name === speciesName);
    if (speciesIdx == -1) {
      console.log('Error: unable to find species for deletion', speciesName);
      return;
    }
    const removedSpecies = workingSpecies[speciesIdx];
    workingSpecies.splice(speciesIdx, 1);
    curSpecies = workingSpecies;
    setSpeciesRedraw(removedSpecies.name+'-deleted');
  }

  const rowHeight = imageSize.height / 3.0;
  const dropExtras = dropable ? {onDrop:dropHandler,onDragOver:dragoverHandler} : {};
   return (
    <React.Fragment>
      <Box id="edit-image-frame" sx={{backgroundColor:'white', padding:'10px', position:'relative'}} {...dropExtras} >
        <img id={imageId} src={url} alt={name} onLoad={() => getImageSize()}
             style={{maxWidth:maxWidth, maxHeight:maxHeight, 
                     filter:'brightness('+brightness+'%) contrast('+contrast+'%) hue-rotate(' + hue + 'deg) saturate(' + saturation + '%)'}} 
        />
        <Stack style={{ position:'absolute', top:(10)+'px', left:10+'px', minWidth:imageSize.width+'px',
                       maxWidth:imageSize.width+'px', width:imageSize.width+'px', minHeight:maxHeight, maxHeight:maxHeight, 
                    }}
        >
          <Grid container direction="row" alignItems="start" justifyContent="start" sx={{minHeight:rowHeight,maxHeight:rowHeight}}>
            <Grid item size={{ xs: 6, sm: 6, md:6 }} sx={{position:'relative'}}>
              <ImageAdjustments isVisible={!!adjustments} onBrightnessChange={adjustBrightness} 
                                onContrastChange={adjustContrast} onHueChange={adjustHue} onSaturationChange={adjustSaturation} />
            </Grid>
            <Grid item size={{ xs: 6, sm: 6, md:6 }} sx={{marginLeft:'auto', cursor:'default'}}>
              <Typography variant="body" sx={{textTransform:'uppercase',color:'grey','&:hover':{color:'white'} }}>
                {name}
              </Typography>
            </Grid>
            <Grid item size={{ xs: 6, sm: 6, md:6 }} sx={{marginLeft:'auto', cursor:'default'}}>
              <div id="image-edit-close" sx={{height:'20px', flex:'1'}} onClick={() => onClose_func()}>
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
              <Grid item size={{ xs: 6, sm: 6, md:6 }} sx={{position:'relative', marginRight:'auto'}}>
                <ArrowBackIosOutlinedIcon fontSize="large" onClick={() => navigation.prev_func()}
                          sx={{backgroundColor:'rgba(255,255,255,0,3)', '&:hover':{backgroundColor:'rgba(255,255,255,0.7)'} }} />
              </Grid>
              <Grid item size={{ xs: 6, sm: 6, md:6 }} sx={{position:'relative', marginLeft:'auto'}}>
                <ArrowForwardIosOutlinedIcon fontSize="large" onClick={() => navigation.next_func()}
                          sx={{backgroundColor:'rgba(255,255,255,0,3)', '&:hover':{backgroundColor:'rgba(255,255,255,0.7)'} }} />
              </Grid>
            </Grid>
            : null
          }
          <Grid container id="image-edit-species" direction="row" alignItems="end" justifyContent="end"
                sx={{minHeight:rowHeight,maxHeight:rowHeight}}
          >
            <Grid item size={{ xs:6, sm:6, md:6 }} sx={{position:'relative', marginRight:'auto',
                  visibility:(curSpecies ? 'visible' : 'hidden')}}>
              {curSpecies.map((curItem) =>
                <ImageEditSpecies key={name+curItem.name} name={curItem.name} count={curItem.count} onCDelete_func={handleSpeciesDelete}
                                  onChange_func={handleInputChange} onBlur_func={handleBlur} />
              )}
            </Grid>
          </Grid>
        </Stack>
      </Box>
    </React.Fragment>
  );
}