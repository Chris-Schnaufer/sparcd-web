/** @module components/ImageAdjustments */

import * as React from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

import InputSlider from './InputSlider';

/**
 * Returns the image adjustment UI
 * @function
 * @param {function} onBrightnessChange Called when brightness value changes
 * @param {function} onContrastChange Called when contrast value changes
 * @param {function} onHueChange Called when hue value changes
 * @param {function} onSaturationChange Called when saturation value changes
 * @returns {object} The UI for image adjustments
 */
export default function ImageAdjustments({isVisible, onBrightnessChange, onContrastChange, onHueChange, onSaturationChange}) {
  const [showAdjustments, setShowAdjustments] = React.useState(false);

  const adjustmentDropProps = showAdjustments ? {writingMode:'vertical-lr', transform:'rotate(-180deg)', paddingTop:'5px',paddingBottom:'5px',color:'black', backgroundColor:'rgba(255,255,255,0.7)'} : 
                                                {paddingLeft:'5px',paddingRight:'5px'};
  return (
    <div style={{visibility:(isVisible ? 'visible':'hidden') }}>
      <Grid id="image-edit-adjustments" container direction="column" alignItems="start" justifyContent="start"
            sx={{position:'absolute',left:'0px',top:'1.3em',
                 visibility:(showAdjustments ? 'visible' : 'hidden')}} >
        <Grid size={{ xs: 6, sm: 6, md:6 }} sx={{backgroundColor:'rgba(255,255,255,0.7)'}}>
          <InputSlider label="Brightness" onChange={onBrightnessChange} />
          <InputSlider label="Contrast" onChange={onContrastChange} />
          <InputSlider label="Hue"  onChange={onHueChange} />
          <InputSlider label="Saturation"  onChange={onSaturationChange} />
        </Grid>
      </Grid>
      <Box id="image-edit-adjust" sx={{position:'absolute',left:'0px',top:'0px',height:'20px', flex:'1'}} 
              onClick={() => setShowAdjustments(!showAdjustments)}>
        <Typography variant="body" sx={{textTransform:'uppercase',color:'darkgrey',backgroundColor:'rgba(255,255,255,0.3)',
                                         padding:'1px 3px 0px 3px',borderRadius:'3px',
                                         '&:hover':{backgroundColor:'rgba(255,255,255,0.7)',color:'black'},
                                         cursor:'pointer', ...adjustmentDropProps
                                       }}>
          &raquo;
        </Typography>
      </Box>
    </div>
  );
}
