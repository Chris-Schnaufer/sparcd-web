/** @module components/InputSlider */

import * as React from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Slider from '@mui/material/Slider';
import { styled } from '@mui/material/styles';
import MuiInput from '@mui/material/Input';

// Width of the input field
const Input = styled(MuiInput)`
  width: 42px;
`;

/**
 * Slider with input field implementation
 * @function
 * @param {string} label The label for the slider
 * @param {function} onChange_func Function to call when the value changes
 * @returns {object} The rendered UI
 */
export default function InputSlider({label, onChange_func}) {
  const [value, setValue] = React.useState(50);

  /**
   * Stores the new value when the slider was changed
   * @function
   * @param {object} event The triggering event
   * @param {int} The new value
   */
  const handleSliderChange = (event, newValue) => {
    setValue(newValue);
    onChange_func(newValue);
  }

  /**
   * Stored the new value when the input field is modified
   * @function
   * @param {object} event The triggering event
   */
  function handleInputChange(event) {
    const newValue = event.target.value === '' ? 0 : Number(event.target.value);
    setValue(newValue);
    onChange_func(newValue);
  }

  /**
   * Adjusts the value boundaries as needed when focus is lost
   * @function
   */
  function handleBlur() {
    if (value < 0) {
      setValue(0);
      onChange_func(0);
    } else if (value > 100) {
      setValue(100);
      onChange_func(100);
    }
  }

  // Return the rendered UI
  return (
    <Box sx={{ width: 300 }}>
      <Grid container spacing={2} sx={{ alignItems: 'center' }}>
        <Grid item xs>
          <Typography id="input-slider" gutterBottom>
            {label}
          </Typography>
        </Grid>
        <Grid item xs>
          <Slider
            value={typeof value === 'number' ? value : 0}
            onChange={handleSliderChange}
            aria-labelledby="input-slider"
          />
        </Grid>
        <Grid item>
          <Input
            value={value}
            size="small"
            onChange={handleInputChange}
            onBlur={handleBlur}
            inputProps={{
              step: 1,
              min: 0,
              max: 100,
              type: 'number',
              'aria-labelledby': 'input-slider',
            }}
          />
        </Grid>
      </Grid>
    </Box>
  );
}

