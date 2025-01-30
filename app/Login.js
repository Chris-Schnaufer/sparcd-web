import Image from 'next/image'
import styles from './page.module.css'
import { useContext, useState } from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import LoginIcon from '@mui/icons-material/Login';
import TextField from '@mui/material/TextField';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

import wildcatResearch from '../public/wildcatResearch.png'
import {urlValid, userValid, passwordValid} from './checkLogin'
import {LoginValidContext} from './checkLogin'

export default function Login({prev_url, prev_user, prev_remember, login_func}) {
  const [showPassword, setShowPassword] = useState(false);
  const [rememberChecked, setRememberChecked] = useState(!!prev_remember);
  const valuesValid = useContext(LoginValidContext);

  const handleClickShowPassword = () => setShowPassword((show) => !show);

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  const handleMouseUpPassword = (event) => {
    event.preventDefault();
  };

  const rememberChanged = (event) => {
    setRememberChecked(event.target.checked);
  }

  function call_login_func() {
    let ctrl = document.getElementById('url_entry');
    const url = ctrl.value;
    ctrl = document.getElementById('username_entry');
    const user = ctrl.value;
    ctrl = document.getElementById('password_entry');
    const password = ctrl.value;
    ctrl = document.getElementById('remember_login_fields');
    const remember = ctrl.checked;

    login_func(url, user, password, remember);
  }

  let inputErrorClass = styles.login_dialog_items_error;

  return (
    <div className={styles.login_background}>
    <div className={styles.login_wrapper}>
      <div className={styles.login_dialog_wrapper}>
        <div className={styles.login_dialog}>
          <Image height='60' alt="Wildcats Research" src={wildcatResearch} placeholder="blur" />
          <div className={styles.login_dialog_items}>
            <Box
              component="form"
              sx={{ '& > :not(style)': { m: 1, width: '37ch' } }}
              noValidate
              autoComplete="off"
            >
              <TextField required 
                    id="url_entry"
                    label="Database URL"
                    defaultValue={prev_url}
                    size="small"
                    error={!valuesValid.url}
                    sx={{m:5}}
                    inputProps={{style: {fontSize: 12}}}
                    slotProps={{
                      inputLabel: {
                        shrink: true,
                      },
                    }}
                    />
              <TextField required 
                    id="username_entry"
                    label="Username"
                    defaultValue={prev_user}
                    size="small"
                    error={!valuesValid.user}
                    sx={{m:5}}
                    inputProps={{style: {fontSize: 12}}}
                    slotProps={{
                      inputLabel: {
                        shrink: true,
                      },
                    }}
                    />
              <TextField required 
                    id="password_entry"
                    label="Password"
                    type={showPassword ? 'text' : 'password'}
                    size="small"
                    error={!valuesValid.password}
                    sx={{m:5}}
                    inputProps={{style: {fontSize: 12}}}
                    slotProps={{
                      inputLabel: {
                        shrink: true,
                      },
                      input: {
                        endAdornment: 
                          <InputAdornment position="end">
                            <IconButton
                              aria-label={
                                showPassword ? 'hide the password' : 'display the password'
                              }
                              onClick={handleClickShowPassword}
                              onMouseDown={handleMouseDownPassword}
                              onMouseUp={handleMouseUpPassword}
                              edge="end"
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>,
                      },
                    }}
                    />
                    <FormGroup>
                      <FormControlLabel 
                        required 
                        size="small"
                        control={<Checkbox id="remember_login_fields" checked={rememberChecked} onChange={rememberChanged} />}
                        label={<span style={{ fontSize: 12, color: "rgba(0, 0, 0, 0.6)" }}>Remember URL and username</span>}
                        />
                    </FormGroup>

            <div className={styles.login_dialog_login_button_wrap}>
              <Button size="small" color="login_button" sx={{bgcolor: 'background.default'}} endIcon={<LoginIcon />} onClick={call_login_func}>Login</Button>
            </div>
            </Box>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
}