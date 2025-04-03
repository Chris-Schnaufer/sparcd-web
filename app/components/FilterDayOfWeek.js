/** @module components/FilterDayOfWeek */

import * as React from 'react';
import BackspaceOutlinedIcon from '@mui/icons-material/BackspaceOutlined';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Checkbox from '@mui/material/Checkbox';
import Grid from '@mui/material/Grid';
import FormGroup from '@mui/material/FormGroup';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import FilterCard from './FilterCard'

// The names of the days to use
const dayNames = [
  'MONDAY',
  'TUESDAY',
  'WEDNESDAY',
  'THURSDAY',
  'FRIDAY',
  'SATURDAY',
  'SUNDAY'
];

/**
 * Adds day of the week information to form data
 * @function
 * @param {object} data The saved data to add to the form
 * @param {object} formData The FormData to add the fields to
 */
export function FilterDayOfWeekFormData(data, formData) {
  formData.append('dayofweek', JSON.stringify(data));
}

/**
 * Returns the UI for filtering by day of the week
 * @param {object} {data} Saved day of the week data
 * @param {function} onClose The handler for closing this filter
 * @param {function} onChange The handler for when the filter data changes
 * @returns {object} The UI specific for filtering by day of the week
 */
export default function FilterDayOfWeek({data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedDays, setSelectedDays] = React.useState(data ? data : dayNames); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  // Set default data if we don't have any
  React.useEffect(() => {
    if (!data) {
      onChange(selectedDays);
    }
  }, [selectedDays]);

  /**
   * Handles selecting all the day of the week choices
   * @function
   */
  function handleSelectAll() {
    setSelectedDays(dayNames);
    onChange(dayNames);
  }

  /**
   * Clears all chosen selections
   * @function
   */
  function handleSelectNone() {
    setSelectedDays([]);
    onChange([]);
  }

  /**
   * Handles the user selecting or deselecting a day of the week
   * @function
   * @param {object} event The triggering event data
   * @param {string} dayName The name of the day to add or remove from the filter
   */
  function handleCheckboxChange(event, dayName) {

    if (event.target.checked) {
      const dayIdx = selectedDays.findIndex((item) => dayName === item);
      // Add the day in if we don't have it already
      if (dayIdx < 0) {
        const curDay = selectedDays;
        curDay.push(dayName);
        setSelectedDays(curDay);
        onChange(curDay);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the day if we have it
      const curDay = selectedDays.filter((item) => item !== dayName);
      if (curDay.length < selectedDays.length) {
        setSelectedDays(curDay);
        onChange(curDay);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  // Return the UI for choosing the day of the week
  return (
    <FilterCard title="Day of Week Filter" onClose={onClose} 
                actions={
                  <React.Fragment>
                    <Button sx={{'flex':'1'}} size="small" onClick={handleSelectAll}>Select All</Button>
                    <Button sx={{'flex':'1'}} size="small" onClick={handleSelectNone}>Select None</Button>
                  </React.Fragment>
                }
    >
      <Grid item sx={{minHeight:'210px', maxHeight:'210px', height:'210px', minWidth:'250px', overflow:'scroll',
                      border:'1px solid black', borderRadius:'5px', paddingLeft:'5px',
                      backgroundColor:'rgb(255,255,255,0.3)'
                    }}>
        <FormGroup>
          { dayNames.map((item) => 
              <FormControlLabel key={'filter-day-' + item}
                                control={<Checkbox size="small" 
                                                   checked={selectedDays.findIndex((curDay) => curDay===item) > -1 ? true : false}
                                                   onChange={(event) => handleCheckboxChange(event,item)}
                                          />} 
                                label={<Typography variant="body2">{item}</Typography>} />
            )
          }
        </FormGroup>
      </Grid>
    </FilterCard>
  );
}
