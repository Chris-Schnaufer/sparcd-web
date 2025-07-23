
/** @module components/TitleBar */

import * as React from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import Link from '@mui/material/Link';
import MenuOutlinedIcon from '@mui/icons-material/MenuOutlined';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import Settings from './Settings';
import styles from './components.module.css';
import { UserSettingsContext } from '../serverInfo';

/**
 * Renders the title bar
 * @function
 * @param {string} [search_title] The optional title of the search field
 * @param {array} [breadcrumbs] An optional list of breadcrumbs to display
 * @param {string} [size] Optionally one of "small" or "full"
 * @param {function} [onSearch] The function to call to perform a search
 * @param {function} [onBreadcrumb] The breadcrumb click handler
 * @param {function} onSettings The settings click handler
 * @param {function} onLogout The handler for the user wanting to logout
 * @returns {object} The rendered UI
 */
export default function TitleBar({search_title, breadcrumbs, size, onSearch, onBreadcrumb, onSettings, onLogout}) {
  const [showSettings, setShowSettings] = React.useState(false);
  const userSettings = React.useContext(UserSettingsContext);  // User display settings
  /**
   * Handles the clicking of the search icon
   * @function
   */
  function clickHandler() {
    const searchEl = document.getElementById("search");
    if (searchEl && searchEl.value) {
      if (onSearch(searchEl.value)) {
        searchEl.value = null;
      }
    }
  }

  /**
   * Handles the Enter key to start a search
   * @function
   * @apram {object} event The event
   */
  function handleSearchChange(event) {
    if (event.key == 'Enter') {
      clickHandler();
    }
  }

  /**
   * Handles the user requesting breadcrumb navigation
   * @function
   * @param {object} navItem The chosen breadcrumb navigation item
   */
  function handleNav(navItem) {
    onBreadcrumb(navItem);
  }

  /**
   * Handles the user requesting settings closure
   * @function
   */
  function handleSettingsClose() {
    setShowSettings(false);
  }

  const extraInputSX = size === "small" ? {maxWidth:'10em'} : {};

  // Render the UI
  return (
    <header id='sparcd-header' className={styles.titlebar} role="banner">
      <Box sx={{ flexGrow: 1, 'width': '100vw' }} >
        <Grid id='sparcd-header-items' container direction="column" spacing={0} sx={{flexGrow:1}}>
          <Grid id='sparcd-header-image-wrapper' container direction="row" spacing={3} sx={{flexGrow:1}}>
            <Grid id='sparcd-header-image-link' size="grow" container direction="row" onClick={() => window.location.href="/"} sx={{cursor:'pointer'}}>
                <div
                  aria-description="Scientific Photo Analysis for Research & Conservation database"
                  className={styles.titlebar_title}>SPARC&apos;d
                </div>
                <img id="sparcd-logo" src="/sparcd.png" alt="SPARC'd Logo" className={styles.titlebar_icon}/>
            </Grid>
            <Grid id='sparcd-header-search-wrapper' sx={{marginLeft:'auto'}} style={{paddingLeft:'0px'}}>
              <Grid id='sparcd-header-search' container direction="row">
                { search_title &&
                  <TextField id="search" label={search_title} placehoder={search_title} size="small" variant="outlined" style={extraInputSX}
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
                }
                <IconButton onClick={() => setShowSettings(true)}>
                  <MenuOutlinedIcon />
                </IconButton>
              </Grid>
            </Grid>
          </Grid>
          <Grid size={{xs:12, sm:12, md:12}} style={{paddingTop:'0', visibility:breadcrumbs ? 'visible':'hidden' }}>
            <Typography sx={{fontSize:"xx-small"}}>
            { breadcrumbs ? 
                breadcrumbs.map((item, idx) => {
                              return (<React.Fragment key={"breadcrumb-" + idx + '-' + item.name} >
                                        &nbsp;
                                        <Link component="button" underline="hover" sx={{fontSize:'larger'}}
                                              onClick={() => handleNav(item)}
                                        >
                                          {item.name}{idx < (breadcrumbs.length -1) ? ' / ' : ' '}
                                        </Link>
                                      </React.Fragment>
                              );}
                            )
              : <React.Fragment>&nbsp;</React.Fragment>
            }
            </Typography>
          </Grid>
        </Grid>
      </Box>
      {showSettings && onSettings != null && <Settings curSettings={userSettings} onChange={onSettings} onClose={handleSettingsClose} 
                                                       onLogout={() => {handleSettingsClose();onLogout();}} />
      }
    </header>
    );
}
