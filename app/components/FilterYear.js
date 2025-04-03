/** @module components/FilterYear */

import * as React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Checkbox from '@mui/material/Checkbox';
import Grid from '@mui/material/Grid';
import FormGroup from '@mui/material/FormGroup';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import InputAdornment from '@mui/material/InputAdornment';
import MenuItem from '@mui/material/MenuItem';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import FilterCard from './FilterCard'

/**
 * Adds year range information to form data
 * @function
 * @param {object} data The saved data to add to the form
 * @param {object} formData The FormData to add the fields to
 */
export function FilterYearFormData(data, formData) {
  formData.append('yearStart', data.start + '');
  formData.append('yearEnd', data.end + '');
  return formData;
}

/**
 * Returns the UI for filtering by year range
 * @param {object} {data} Saved year data
 * @param {function} onClose The handler for closing this filter
 * @param {function} onChange The handler for when the filter data changes
 * @returns {object} The UI specific for filtering by year range
 */
export default function FilterYear({data, onClose, onChange}) {
  const theme = useTheme();
  const curYear = new Date().getFullYear();
  const [selectedYearEnd, setSelectedYearEnd] = React.useState(data ? data.start : curYear); // The user's end year
  const [selectedYearStart, setSelectedYearStart] = React.useState(data ? data.end : curYear); // The user's start year
  const [yearEndError, setYearEndError] = React.useState(false); // The user's end year is in error
  const [yearStartError, setYearStartError] = React.useState(false); // The user's start year is in error

  // Set the default data if it's not set yet
  React.useEffect(() => {
    if (!data) {
      onChange({start:selectedYearStart, end:selectedYearEnd});
    }
  }, [selectedYearStart,selectedYearEnd]);

  /**
   * Handles the starting year changing
   * @function
   * @param {object} event The triggering event data
   */
  function handleYearStartChange(event) {
    const newYear = parseInt(event.target.value);
    setSelectedYearStart(newYear);
    if (newYear <= selectedYearEnd || newYear.length > 4) {
      setYearStartError(false);
      onChange({start:newYear, end:selectedYearEnd});
    } else {
      setYearStartError(true);
    }
  }

  /**
   * Handles the ending year changing
   * @function
   * @param {object} event The triggering event data
   */
  function handleYearEndChange(event) {
    const newYear = parseInt(event.target.value);
    setSelectedYearEnd(newYear);
    if (newYear >= selectedYearStart || newYear.length > 4) {
      setYearEndError(false);
      onChange({start:selectedYearStart, end:newYear});
    } else {
      setYearEndError(true);
    }
  }

  // Return the UI for filtering by year
  return (
    <FilterCard title="Year Filter" onClose={onClose} >
      <Grid item sx={{minHeight:'230px', maxHeight:'230px', height:'230px', minWidth:'250px', maxWidth:'250px',
                      overflowX:'clip', overflowY:'scroll', paddingLeft:'5px', backgroundColor:'rgb(255,255,255,0.3)'
                    }}>
        <Stack spacing={1}>
          <TextField id="start-year-value" error={yearStartError ? true : false} value={selectedYearStart} type="numeric" label="Start Year" variant="standard" 
                     onChange={handleYearStartChange}
          />
          <Typography gutterBottom variant="body2" noWrap sx={{textAlign:'center'}}>
            Up to, and including
          </Typography>
          <TextField id="end-year-value" error={yearEndError ? true : false} value={selectedYearEnd} type="numeric" label="End Year" variant="standard" 
                     onChange={handleYearEndChange}
          />
          <Typography gutterBottom variant='body2' color='error' sx={{textAlign:'start'}}>
            { yearStartError || yearEndError ? 'End year must be equal or greater than start year' : ''}
          </Typography>
        </Stack>
      </Grid>
    </FilterCard>
  );
}
