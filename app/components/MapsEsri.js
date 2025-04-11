'use client'

/** @module components/MapsEsri */

import * as React from 'react';

import '@arcgis/map-components/dist/components/arcgis-legend';
import '@arcgis/map-components/dist/components/arcgis-map';
import '@arcgis/map-components/dist/components/arcgis-zoom';
import Collection from "@arcgis/core/core/Collection";
import Extent from "@arcgis/core/geometry/Extent";
import FeatureLayer from "@arcgis/core/layers/FeatureLayer";
import GraphicsLayer from "@arcgis/core/layers/GraphicsLayer";
import Graphic from "@arcgis/core/Graphic";
import Map from "@arcgis/core/Map";
import MapView from "@arcgis/core/views/MapView";
import Point from "@arcgis/core/geometry/Point";
import ValuePicker from "@arcgis/core/widgets/ValuePicker";
import ValuePickerCombobox from "@arcgis/core/widgets/ValuePicker/ValuePickerCombobox";
import * as reactiveUtils from "@arcgis/core/core/reactiveUtils";

import { LocationsInfoContext } from '../serverInfo'

export default function MapsEsri({extent, center, mapName, mapChoices, onChange, top, width, height}) {
  const locationItems = React.useContext(LocationsInfoContext);
  const mapRef = React.useRef();
  const [configureReady, setConfigureReady] = React.useState(false);
  const [layerCollection, setLayerCollection] = React.useState(null);

  let addLayerCount = 0;

  React.useLayoutEffect(() => {
    if (typeof window !== 'undefined')
      window.setTimeout(() => setConfigureReady(true), 500);
  }, [setConfigureReady]);

  React.useLayoutEffect(() => { // NEW
    const mapEl = document.getElementById('viewDiv');
    if (mapEl) {
      const layers = getLocationLayer();
      const map = new Map({basemap:mapName, layers:layers});

      let curMapName = mapChoices.find((item) => item.config.mapName === mapName);
      curMapName = curMapName ? curMapName.value : mapChoices[0].value;

      const collectionNames = mapChoices.map((item) => {return {label:item.name, value:item.value};});
      const valuePicker = new ValuePicker({
        visibleElements: {
          nextButton: false,
          playButton: false,
          previousButton: false
        },
        component: {
          type: "combobox", // autocasts to ValuePickerCombobox
          placeholder: "Map Type",
          items: collectionNames
        },
        values: [curMapName],
        visible: true
      });

      reactiveUtils.watch(
        () => valuePicker.values,
        (values) => onChange(values[0])
      );

      const view = new MapView({
        map: map,
        container: 'viewDiv',
        center: center,
        zoom: 7
      });

      // add the UI components to the view
      view.ui.add(valuePicker, "top-right");

    }
  } ,[mapName]);

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
    /*
         view.hitTest(event).then(function (response) { 
           if (response.results.length) { 
             var graphic = response.results.filter(function (result) { 
               // check if the graphic belongs to the layer of interest 
               return result.graphic.layer === featureLayer; 
             })[0].graphic; 
             view.popup.open({ 
               location: graphic.geometry.centroid, 
               features: [graphic] 
             }); 
           } else { 
             view.popup.close(); 
           } 
         }); 
       }); 
     }); 
    */
  }

  const curExtent = new Extent({xmin:extent[0].x, xmax:extent[1].x, ymin:extent[1].y, ymax:extent[0].y, zoom:7});
  return ( // NEW
    <React.Fragment>
      <div id="viewDiv" style={{width:width+'px', maxWidth:width+'px', height:height+'px', maxHeight:height+'px', position:'absolute', top:top+'px'}} >
      </div>
    </React.Fragment>
  );
}
