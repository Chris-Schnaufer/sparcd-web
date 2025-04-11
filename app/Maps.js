/** @module Maps */

import * as React from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import { useTheme } from '@mui/material/styles';

//import MapsEsri from './components/MapsEsri';
import * as utils from './utils';


const MapsEsriLazyload = React.lazy(() => import('./components/MapsEsri'));


/**
 * Provides the UI for displaying maps
 * @function
 * @returns {object} The UI for showing maps
 */
export default function Queries() {
  const theme = useTheme();
  const [curMapChoice, setCurMapChoice] = React.useState(null); // The current map to display
  const [serverURL, setServerURL] = React.useState(utils.getServer());  // The server URL to use
  const [totalHeight, setTotalHeight] = React.useState(null);  // Default value is recalculated at display time
  const [windowSize, setWindowSize] = React.useState({width: 640, height: 480});  // Default values are recalculated at display time
  const [workingTop, setWorkingTop] = React.useState(null);    // Default value is recalculated at display time
  const [workspaceWidth, setWorkspaceWidth] = React.useState(640);  // Default value is recalculated at display time
  const extent = [{x:-109.0, y:36.0}, {x:-115.0, y:30.0}];
  const center = {x:-110.9742, y:32.2540}

  const mapChoices = [
    {provider:'esri', name:'Esri World Street Map', value:'streets-vector', config:{mapName:'streets-vector'}},
    {provider:'esri', name:'Esri World Topo Map', value:'topo-vector', config:{mapName:'topo-vector'}},
    {provider:'esri', name:'Esri World Imagery', value:'satelliteå', config:{mapName:'satellite'}},
  ];

/*
  OpenTopoMap("Open Topo Map", "https://opentopomap.org/about", new MapTileLayer("OpenTopoMap", "https://{c}.tile.opentopomap.org/{z}/{x}/{y}.png", 0, 17)),
  EsriWorldStreetMap("Esri World Street Map", "https://www.esri.com/en-us/home", new MapTileLayer("EsriWorldStreetMap", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", 0, 19)),
  EsriWorldTopoMap("Esri World Topo Map", "https://www.esri.com/en-us/home", new MapTileLayer("EsriWorldTopoMap", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}", 0, 19)),
  EsriWorldImagery("Esri World Imagery", "https://www.esri.com/en-us/home", new MapTileLayer("EsriWorldImagery", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", 0, 19));
*/

  // Recalcuate available space in the window
  React.useLayoutEffect(() => {
    const newSize = {'width':window.innerWidth,'height':window.innerHeight};
    setWindowSize(newSize);
    calcTotalSize(newSize);
    setWorkspaceWidth(newSize.width);
  }, [totalHeight, workingTop, workspaceWidth]);

  // Adds a handler for when the window is resized, and automatically removes the handler
  React.useLayoutEffect(() => {
      function onResize () {
        const newSize = {'width':window.innerWidth,'height':window.innerHeight};

        setWindowSize(newSize);

        calcTotalSize(newSize);

        const newWorkspaceWidth = newSize.width;
        setWorkspaceWidth(newWorkspaceWidth);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, [totalHeight, workingTop, workspaceWidth]);

  /**
   * Calculates the total UI size available for the workarea
   * @function
   * @param {object} curSize The total width and height of the window
   */
  function calcTotalSize(curSize) {
    const elWorkspace = document.getElementById('maps-workspace-wrapper');
    if (elWorkspace) {
      const elWorkspaceSize = elWorkspace.getBoundingClientRect();
      setTotalHeight(elWorkspaceSize.height);
      setWorkingTop(0);
    }

    setWorkspaceWidth(curSize.width);
  }

  function handleMapChanged(newMapValue) {
    const newChoice = mapChoices.find((item) => item.value === newMapValue);
    setCurMapChoice(newChoice);
  }

  if (!curMapChoice) {
    setCurMapChoice(mapChoices[0]);
  }

  // Return the UI
  const curHeight = totalHeight + 'px';
  return (
    <Box id='maps-workspace-wrapper' sx={{ flexGrow: 1, 'width': '100vw', position:'relative'}} >
      {curMapChoice && curMapChoice.provider === 'esri' 
          && <MapsEsriLazyload extent={extent} center={center} top={workingTop} width={workspaceWidth} height={totalHeight}
                               mapChoices={mapChoices} {...curMapChoice.config} onChange={handleMapChanged}
              />
      }
   </Box>
  );
}