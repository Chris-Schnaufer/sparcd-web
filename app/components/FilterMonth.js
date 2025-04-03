/** @module components/FilterMonth */

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

// The names of the month to use
const monthNames = [
  'JANUARY',
  'FEBRUARY',
  'MARCH',
  'APRIL',
  'MAY',
  'JUNE',
  'JULY',
  'AUGUST',
  'SEPTEMBER',
  'OCTOBER',
  'NOVEMBER',
  'DECEMBER'
];

/**
 * Adds month information to form data
 * @function
 * @param {object} data The saved data to add to the form
 * @param {object} formData The FormData to add the fields to
 */
export function FilterMonthFormData(data, formData) {
  formData.append('month', JSON.stringify(data));
}

/**
 * Returns the UI for filtering by month
 * @param {object} {data} Saved month data
 * @param {function} onClose The handler for closing this filter
 * @param {function} onChange The handler for when the filter data changes
 * @returns {object} The UI specific for filtering by month
 */
export default function FilterMonth({data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedMonths, setSelectedMonths] = React.useState(data ? data : monthNames); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  // Set hte default data if we don't have any
  React.useEffect(() => {
    if (!data) {
      onChange(selectedMonths);
    }
  }, [selectedMonths]);

  /**
   * Handle selecting all the filter choices
   * @function
   */
  function handleSelectAll() {
    setSelectedMonths(monthNames);
    onChange(monthNames);
  }

  /**
   * Handles clearing all the filter choices
   * @function
   */
  function handleSelectNone() {
    setSelectedMonths([]);
    onChange([]);
  }

  /**
   * Handles the user selecting or deselecting an month
   * @function
   * @param {object} event The triggering event data
   * @param {string} monthName The name of the month to add or remove from the filter
   */
  function handleCheckboxChange(event, monthName) {

    if (event.target.checked) {
      const monthIdx = selectedMonths.findIndex((item) => monthName === item);
      // Add the month in if we don't have it already
      if (monthIdx < 0) {
        const curMonths = selectedMonths;
        curMonths.push(monthName);
        setSelectedMonths(curMonths);
        onChange(curMonths);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the month if we have it
      const curMonths = selectedMonths.filter((item) => item !== monthName);
      if (curMonths.length < selectedMonths.length) {
        setSelectedMonths(curMonths);
        onChange(curMonths);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  // Return the UI for the month filter
  return (
    <FilterCard title="Month Filter" onClose={onClose} 
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
          { monthNames.map((item) => 
              <FormControlLabel key={'filter-months-' + item}
                                control={<Checkbox size="small" 
                                                   checked={selectedMonths.findIndex((curMonth) => curMonth===item) > -1 ? true : false}
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
