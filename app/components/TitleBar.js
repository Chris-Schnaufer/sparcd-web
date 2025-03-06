
import * as React from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import TextField from '@mui/material/TextField';

import styles from './components.module.css'

export default function TitleBar({search_title, search_func}) {

  function clickHandler() {
    const searchEl = document.getElementById("search");
    if (searchEl && searchEl.value) {
      search_func(searchEl.value);
    }
  }

  function handleSearchChange(ev) {
    if (ev.key == 'Enter') {
      clickHandler();
    }
  }

  return (
    <header id='sparcd-header' className={styles.titlebar} role="banner">
      <Box sx={{ flexGrow: 1, 'width': '100vw' }} >
        <Grid container spacing={3} sx={{flexGrow:1}}>
          <Grid item size={{xs:12, sm:12, md:12}}>
            <Grid container direction="row">
                <div
                  aria-description="Scientific Photo Analysis for Research & Conservation database"
                  className={styles.titlebar_title}>SPARC&apos;d
                </div>
                <img src="/sparcd.png" alt="SPARC'd Logo"/>
            </Grid>
          </Grid>
          <Grid item size={{xs:12, sm:12, md:12}} offset={{xs:'auto', sm:'auto', md:'auto'}} sx={{marginLeft:'auto'}}>
            { search_title ?
              <TextField id="search" label={search_title} placehoder={search_title} size="small" variant="outlined"
                        onKeyPress={handleSearchChange}
                        slotProps={{
                          input: {
                            endAdornment:
                              <InputAdornment position="end">
                                <IconButton
                                  aria-label="description for action"
                                  onClick={clickHandler}
                                >
                                  <SearchOutlinedIcon />
                                </IconButton>
                              </InputAdornment>
                          },
                        }}
             />
              : null
            }
          </Grid>
        </Grid>
      </Box>
    </header>
    );
}
