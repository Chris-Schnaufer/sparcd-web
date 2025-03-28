/** @module components/FilterSpecies */

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

import { SpeciesInfoContext } from '../serverInfo'

export default function FilterSpecies({data, onClose, onChange}) {
  const theme = useTheme();
  const speciesItems = React.useContext(SpeciesInfoContext);
  const [displayedSpecies, setDisplayedSpecies] = React.useState(speciesItems); // The visible species
  const [selectedSpecies, setSelectedSpecies] = React.useState(data ? data : []); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  function handleSelectAll() {
    const curSpecies = displayedSpecies.map((item) => item.name);
    const newSpecies = curSpecies.filter((item) => selectedSpecies.findIndex((selItem) => selItem === item) < 0);
    const updatedSelections = [...selectedSpecies, ...newSpecies];
    setSelectedSpecies(updatedSelections);
    onChange(updatedSelections);
    handleClearSearch();
  }

  function handleSelectNone() {
    setSelectedSpecies([]);
    onChange([]);
    handleClearSearch();
  }

  function handleCheckboxChange(event, speciesName) {

    if (event.target.checked) {
      const speciesIdx = selectedSpecies.findIndex((item) => speciesName === item);
      // Add the species in if we don't have it already
      if (speciesIdx < 0) {
        const curSpecies = selectedSpecies;
        curSpecies.push(speciesName);
        setSelectedSpecies(curSpecies);
        onChange(curSpecies);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the species if we have it
      const curSpecies = selectedSpecies.filter((item) => item !== speciesName);
      if (curSpecies.length < selectedSpecies.length) {
        setSelectedSpecies(curSpecies);
        onChange(curSpecies);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  function handleSearchChange(event) {
    if (event.target.value) {
      const ucSearch = event.target.value.toUpperCase();
      setDisplayedSpecies(speciesItems.filter((item) => item.name.toUpperCase().includes(ucSearch)));
    } else {
      setDisplayedSpecies(speciesItems);
    }
  }

  function handleClearSearch() {
    const searchEl = document.getElementById('file-species-search');
    if (searchEl) {
      searchEl.value = '';
      setDisplayedSpecies(speciesItems);
    }
  }

  return (
    <Card id="filter-species" sx={{backgroundColor:'seashell', border:"none", boxShadow:"none"}}>
      <CardHeader title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid item>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          Species Filter
                        </Typography>
                      </Grid>
                      <Grid item sx={{marginLeft:'auto'}} >
                        <div onClick={onClose}>
                          <Tooltip title="Delete this filter">
                            <Typography gutterBottom variant="body2" noWrap="true"
                                        sx={{textTransform:'uppercase',
                                        color:'grey',
                                        cursor:'pointer',
                                        fontWeight:'500',
                                        backgroundColor:'rgba(0,0,0,0.03)',
                                        padding:'3px 3px 3px 3px',
                                        borderRadius:'3px',
                                        '&:hover':{backgroundColor:'rgba(255,255,255,0.7)', color:'black'}
                                     }}
                            >
                                X
                            </Typography>
                          </Tooltip>
                        </div>
                      </Grid>
                    </Grid>
                    }
                style={{paddingTop:'0px', paddingBottom:'0px'}}
      />
      <CardContent sx={{paddingTop:'0px', paddingBottom:'0px'}}>
          <Grid item sx={{minHeight:'160px', maxHeight:'160px', height:'160px', minWidth:'250px', overflow:'scroll',
                          border:'1px solid black', borderRadius:'5px', paddingLeft:'5px',
                          backgroundColor:'rgb(255,255,255,0.3)'
                        }}>
            <FormGroup>
              { displayedSpecies.map((item) => 
                  <FormControlLabel key={'filter-species-' + item.name}
                                    control={<Checkbox size="small" 
                                                       checked={selectedSpecies.findIndex((curSpecies) => curSpecies===item.name) > -1 ? true : false}
                                                       onChange={(event) => handleCheckboxChange(event,item.name)}
                                              />} 
                                    label={<Typography variant="body2">{item.name}</Typography>} />
                )
              }
            </FormGroup>
          </Grid>
          <FormControl fullWidth variant="standard">
            <TextField
              variant="standard"
              id="file-species-search"
              label="Search"
              slotProps={{
                input: {
                  endAdornment:(
                    <InputAdornment position="end">
                      <IconButton onClick={handleClearSearch}>
                        <BackspaceOutlinedIcon/>
                      </IconButton>
                    </InputAdornment>
                  )
                },
              }}
              onChange={handleSearchChange}
            />
          </FormControl>
      </CardContent>
      <CardActions>
              <Button sx={{'flex':'1'}} size="small" onClick={handleSelectAll}>Select All</Button>
              <Button sx={{'flex':'1'}} size="small" onClick={handleSelectNone}>Select None</Button>
      </CardActions>
    </Card>
  );
}
