'use client'

/** @module components/MapsEsri */

import * as React from 'react';

import '@arcgis/map-components/dist/components/arcgis-legend';
import '@arcgis/map-components/dist/components/arcgis-map';
import '@arcgis/map-components/dist/components/arcgis-zoom';
import Collection from "@arcgis/core/core/Collection";
import Extent from "@arcgis/core/geometry/Extent";
import GraphicsLayer from "@arcgis/core/layers/GraphicsLayer";
import Graphic from "@arcgis/core/Graphic";
import Point from "@arcgis/core/geometry/Point";

import { LocationsInfoContext } from '../serverInfo'

export default function MapsEsri({extent, mapName}) {
  const locationItems = React.useContext(LocationsInfoContext);
  const mapRef = React.useRef();
  const [configureReady, setConfigureReady] = React.useState(false);
  const [layerCollection, setLayerCollection] = React.useState(null);

  let addLayerCount = 0;

  React.useLayoutEffect(() => {
    if (typeof window !== 'undefined')
      window.setTimeout(() => setConfigureReady(true), 500);
  }, [setConfigureReady]);

  React.useLayoutEffect(() => {
    window.setTimeout(addLayer, 500);
  }, [layerCollection]);

  function addLayer() {
    const arcgisMap = document.querySelector("arcgis-map");
    if (arcgisMap != null) {
      console.log('MAP:', arcgisMap.view);
      //arcgisMap.view.on("pointer-move", onMouseOverPopup);
      const collection = getLocationLayer();
      collection.forEach((layer) => arcgisMap.map.add(layer));
    } else {
      addLayerCount += 1;
      if (addLayerCount < 20) {
        window.setTimeout(addLayer, 500);
      }
    }
  }

  function getLocationLayer() {
    let curCollection = layerCollection || [];
    if (!layerCollection) {
      let features = locationItems.map((item, idx) => 
        new Graphic({
                geometry: new Point({x:parseFloat(item.lngProperty),
                                     y:parseFloat(item.latProperty), 
                                     z:parseFloat(item.elevationProperty)
                                   }),
                symbol: {
                  type: "simple-marker", // autocasts as new SimpleMarkerSymbol()
                  color: "blue",
                  size: 8,
                  outline: { // autocasts as new SimpleLineSymbol()
                    width: 0.5,
                    color: "darkblue"
                  }
                },
                attributes: {...item, ...{objectId: idx}},
                popupTemplate: {
                  title: item.idProperty,
                  content: [{
                      type: 'fields',
                      fieldInfos: [
                        {
                          fieldName: 'nameProperty',
                          label: 'Name',
                          visible: true,
                        },
                        {
                          fieldName: 'latProperty',
                          label: 'Latitude',
                          visible: true,
                        },
                        {
                          fieldName: 'lngProperty',
                          label: 'Longitude',
                          visible: true,
                        },
                        {
                          fieldName: 'elevationProperty',
                          label: 'Elevation',
                          visible: true,
                        }
                      ]
                    }]
                }
              })
      );

      let layer = new GraphicsLayer({graphics: features});

      curCollection.push(layer);
      setLayerCollection(curCollection);
    }

    return curCollection;
  }

  function onMouseOverPopup(event) { 
    // See: https://support.esri.com/en-us/knowledge-base/how-to-display-pop-ups-using-a-mouse-hover-in-arcgis-ap-000024297
  }

/*
            <arcgis-legend position="bottom-left"></arcgis-legend>
*/

  const curExtent = new Extent({xmin:extent[0].x, xmax:extent[1].x, ymin:extent[1].y, ymax:extent[0].y, zoom:7});
  return (
    <React.Fragment>
      { configureReady && 
          <arcgis-map
            basemap={mapName}
            extent={curExtent}
            onPointerMove={onMouseOverPopup}
          >
            <arcgis-zoom position="top-left"></arcgis-zoom>
          </arcgis-map>
      }
    </React.Fragment>
  );
}
