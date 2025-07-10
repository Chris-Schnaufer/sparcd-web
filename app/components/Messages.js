'use client'

/** @module Messages */

import * as React from 'react';
import ErrorOutlineOutlinedIcon from '@mui/icons-material/ErrorOutlineOutlined';
import Grid from '@mui/material/Grid';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import Typography from '@mui/material/Typography';
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined';
import { useTheme } from '@mui/material/styles';

import { SizeContext } from '../serverInfo'

let messageId = 0;		// Sequential message ID for messages

const LevelColors = {error: {background:'rgba(255, 230, 230, 0.83)', color:'black'},
                     warning: {background:'rgba(255, 250, 190, 0.83)', color:'black'},
                     information: {background:'rgba(235, 255, 255, 0.83)', color:'black'},
                    }

const LevelValues = ['error','warning','information'];    // Keep lowercase
const LevelDisplay = ['Error','Warning','Information'];   // Levels for display

// The message level values
export const Level = {
	Error: LevelValues[0],
	Warning: LevelValues[1],
	Warn: LevelValues[1],
	Info: LevelValues[2],
	Information: LevelValues[2]
}

/**
 * Creates a message object
 * @function
 * @param {string} level The level as defined in Level (e.g.: Level.Error)
 * @param {string} message The actual message to display
 * @return {object} A message object
 */
export function makeMessage(level, message, title) {
	// Check the level to see if it's a valid value
	const levelLower = level.toLowerCase();
	if (!LevelValues.find((item) => item === levelLower)) {
		levelLower = undefined;
	}

  // Check for a title
  if (!title) {
    if (levelLower) {
      title = LevelDisplay[LevelValues.indexOf(levelLower)];
    } else {
      title = LevelDisplay[LevelValues.indexOf('information')];
    }
  }

	// Return the message object
	return {level: level ? levelLower : Level.Information,
			message: message + '',
      title: title,
			messageId: ++messageId,
      close: false
			}
}

/**
 * Provides the UI for messages
 * @function
 * @param {object} messages The array of message objects to display
 * @param {number} {maessagesMax} The maximum number of messages to display at one time (default is 3)
 * @param {number} {maessagesTimeout} The number of seconds before a message times out
 * @param {function} {close_cd} Function to call upon the message closing
 * @returns {object} The UI for messages
 */
export function Messages({messages, messagesMax, messagesTimeout, close_cb}) {
 	const theme = useTheme();
	const uiSizes = React.useContext(SizeContext);

	if (!messages) {
		return null;
	}

	// Figure out the maximum number of messages
	if (!messagesMax || typeof(messagesMax) !== 'number' || messagesMax < 1) {
		messagesMax = 3;
	}
	messagesMax = Math.min(messages.length, messagesMax);

	// Figure out the timeout
	if (!messagesTimeout || typeof(messagesTimeout) !== 'number') {
		messagesTimeout = 3;
	}

	// If we have a callback, make sure it's a function
	if (!close_cb || typeof(close_cb) !== 'function') {
		close_cb = (msgId) => {const el=document.getElementById("sparcd-message-"+msgId); if (el) el.style.display='none';};
	}

  console.log('HACK:MESSAGE:',theme);
	return ( 
		<React.Fragment>
		{
			messages.slice(0, messagesMax).reverse().map((item, idx) => {
        // Check for messages that are closed
        if (item.closed) {
          return null;
        }

        // Setup the auto-removal of the message
        if (typeof(window) !== "undefined") {
          window.setTimeout(() => close_cb(item.messageId), 6000);
        }

				return (
          <Grid id={"sparcd-message-" + item.messageId} key={"message" + item.messageId} container direction="column" 
                sx={{position:'absolute', marginTop:((15*idx)+5)+'px', marginLeft:((15*idx))+'px', 
                     color:LevelColors[item.level].color, backgroundColor:LevelColors[item.level].background, 
                     padding:'10px', minWidth:'50vw', maxWidth:'90vw',
                     border:'1px solid black', borderRadius:'10px'
                    }}>
            <Grid id={"sparcd-message-titlebar-" + item.messageId} container direction="row" alignitem="start" justifyContent="space-between">
              {item.level === Level.Error && <ErrorOutlineOutlinedIcon size={2} />}
              {item.level === Level.Warning && <WarningAmberOutlinedIcon size={2} />}
              {item.level === Level.Information && <InfoOutlinedIcon size={2} />}
              <Typography gutterBottom variant="H4" size={8} sx={{fontWeight:'bold'}} >
                {item.title}
              </Typography>
              <Typography gutterBottom variant="body" size={2} onClick={()=>close_cb(item.messageId)} sx={{cursor:'pointer'}} >
                  X
              </Typography>
            </Grid>
            <Grid container direction="row" alignItems="center" justifyContent="space-between">
              <Typography gutterBottom variant="body" sx={{paddingTop:'20px'}} >
                {item.message}
              </Typography>
            </Grid>
					</Grid>
				);
			})
		}
		</React.Fragment>
	);
}
