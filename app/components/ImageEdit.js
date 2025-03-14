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

import { SpeciesInfoContext } from '../serverInfo'
import InputSlider from './InputSlider'

// Width of the input field
const Input = styled(MuiInput)`
  width: 42px;
`;

export default function ImageEdit({url, name, parentId, maxWidth, maxHeight, onClose_func, adjustments, navigation, species, speciesChange_func}) {
  const speciesItems = React.useContext(SpeciesInfoContext);
  const [brightness, setBrightness] = React.useState(100);
  const [contrast, setContrast] = React.useState(100);
  const [speciesRedraw, setSpeciesRedraw] = React.useState(null);
  const [hue, setHue] = React.useState(0);    // From 360 to -360
  const [imageSize, setImageSize] = React.useState({width:40,height:40,top:0,left:0,right:40});
  const [showAdjustments, setShowAdjustments] = React.useState(false);
  const [saturation, setSaturation] = React.useState(100);
  const [imageId, setImageId] =  React.useState('image-edit-image-'+Math.random());
  const brightnessRange = {'default':100, 'min':0, 'max':200};
  const contrastRange = {'default':100, 'min':0, 'max':200};
  const hueRange = {'default':0, 'min':-720, 'max':720};
  const saturationRange = {'default':100, 'min':0, 'max':200};

  let curSpecies = species;

  getImageSize = getImageSize.bind(ImageEdit);

  React.useLayoutEffect(() => {
      function onResize () {
        getImageSize();
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  React.useEffect(() => {
    function onKeypress(event) {
      if (event.key !== 'Meta') {
        console.log('E',event);
        const speciesKeyItem = speciesItems.find((item) => item.keyBinding == event.key.toUpperCase());
        if (speciesKeyItem) {
          const haveSpeciesIdx = curSpecies.findIndex((item) => item.name === speciesKeyItem.name);
          console.log('CS1',curSpecies);
          if (haveSpeciesIdx > -1) {
            curSpecies[haveSpeciesIdx].count = parseInt(curSpecies[haveSpeciesIdx].count) + 1;
            setSpeciesRedraw(curSpecies[haveSpeciesIdx].name+curSpecies[haveSpeciesIdx].count);
          } else {
            curSpecies.push({name:speciesKeyItem.name,count:1});
            setSpeciesRedraw(speciesKeyItem.name+'1');
          }
          console.log('CS2',curSpecies);
        }
        event.preventDefault();
      }
    }
    document.addEventListener("keydown", onKeypress);

    return () => {
      document.removeEventListener("keydown", onKeypress);
    }
  }, []);

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

  console.log(speciesRedraw);
  const rowHeight = imageSize.height / 3.0;
  return (
    <React.Fragment>
      <Box id="edit-image-frame" sx={{backgroundColor:'white', padding:'10px', position:'relative'}} >
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
            { adjustments ?
              <React.Fragment>
                <Box id="image-edit-adjust" sx={{position:'absolute',left:'0px',top:'0px',height:'20px', flex:'1', visibility:(showAdjustments ? 'hidden' : 'visible')}} 
                        onClick={() => setShowAdjustments(!showAdjustments)}>
                  <Typography variant="body" sx={{textTransform:'uppercase',color:'darkgrey',backgroundColor:'rgba(255,255,255,0.3)',
                                                   padding:'1px 3px 0px 3px',borderRadius:'3px',
                                                   '&:hover':{backgroundColor:'rgba(255,255,255,0.7)',color:'black'},
                                                   cursor:'pointer'
                                                 }}>
                    &raquo;
                  </Typography>
                </Box>
                <Grid id="image-edit-adjustments" container direction="column" alignItems="start" justifyContent="start"
                      sx={{position:'absolute',left:'0px',top:'0px',
                           visibility:(showAdjustments ? 'visible' : 'hidden')}} >
                  <Grid item size={{ xs: 6, sm: 6, md:6 }} sx={{backgroundColor:'rgba(255,255,255,0.7)'}}>
                    <InputSlider label="Brightness" onChange_func={adjustBrightness} />
                    <InputSlider label="Contrast" onChange_func={adjustContrast} />
                    <InputSlider label="Hue"  onChange_func={adjustHue} />
                    <InputSlider label="Saturation"  onChange_func={adjustSaturation} />
                  </Grid>
                  <Grid item onClick={() => setShowAdjustments(!showAdjustments)}>
                    <Typography variant="body" sx={{textTransform:'uppercase',color:'black',backgroundColor:'rgba(255,255,255,0.7)',
                                                     marginTop:'0px',
                                                     padding:'1px 1px 0px 1px',borderRadius:'3px',
                                                     '&:hover':{backgroundColor:'rgba(255,255,255,0.7)',color:'black'},
                                                     writingMode:'vertical-lr', transform:'rotate(-180deg)',
                                                     cursor:'default'
                                                   }}>
                      &raquo;
                    </Typography>
                  </Grid>
                </Grid>
              </React.Fragment>
              : null
            }
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
              <ArrowBackIosOutlinedIcon fontSize="large" onClick={() => {console.log('PREV IMAGE');navigation.prev_func();}}
                        sx={{backgroundColor:'rgba(255,255,255,0,3)', '&:hover':{backgroundColor:'rgba(255,255,255,0.7)'} }} />
            </Grid>
            <Grid item size={{ xs: 6, sm: 6, md:6 }} sx={{position:'relative', marginLeft:'auto'}}>
              <ArrowForwardIosOutlinedIcon fontSize="large" onClick={() => {console.log('NEXT IMAGE');navigation.next_func();}}
                        sx={{backgroundColor:'rgba(255,255,255,0,3)', '&:hover':{backgroundColor:'rgba(255,255,255,0.7)'} }} />
            </Grid>
          </Grid>
          : null
        }
        { curSpecies ?
          <Grid container id="image-edit-species" direction="row" alignItems="end" justifyContent="end"
                sx={{minHeight:rowHeight,maxHeight:rowHeight}}
          >
            <Grid item size={{ xs:6, sm:6, md:6 }} sx={{position:'relative', marginRight:'auto'}}>
              {curSpecies.map((curItem) =>
                <Grid id={'image-edit-species-'+curItem.name} key={'image-edit-species-'+curItem.name} container direction="row"
                      sx={{padding:'0px 5px 0px 5px', width:'200px', color:'#4f4f4f',
                         backgroundColor:'rgba(255,255,255,0.3)', '&:hover':{backgroundColor:'rgba(255,255,255,0.7)',color:'black'},
                         borderRadius:'5px', minWidth:'400px'
                      }}
                >
                  <Grid item size={{ xs:6, sm:6, md:6 }} sx={{flex:'6', position:'relative', marginRight:'auto'}}>
                    <Grid container direction="row">
                      <Grid item>
                          <Typography id={"species-name-"+curItem.name} variant="body" sx={{textTransform:'Capitalize',color:'inherit'}}>
                            {curItem.name}
                          </Typography>
                      </Grid>
                      <Grid item sx={{marginLeft:'auto'}}>
                          <Input
                            value={curItem.count}
                            size="small"
                            onChange={(event) => handleInputChange(event, curItem.name)}
                            onBlur={(event) => handleBlur(event, curItem.name)}
                            inputProps={{
                              step: 1,
                              min: 0,
                              max: 100,
                              type: 'number',
                              'aria-labelledby':"species-name-"+curItem.name,
                            }}
                            sx={{flex:'6', position:'relative', marginleft:'auto', color:'inherit'}}
                          />
                      </Grid>
                    </Grid>
                  </Grid>
                  <Grid item size={{ xs:1, sm:1, md:1 }} sx={{flex:'1', position:'relative', marginLeft:'auto'}}>
                    <HighlightOffOutlinedIcon color='inherit' onClick={() => handleSpeciesDelete(curItem.name)}/>
                  </Grid>
                </Grid>
              )}
            </Grid>
          </Grid>
          :null
        }
        </Stack>
      </Box>
    </React.Fragment>
  );
}