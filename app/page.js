'use client'

import { useState } from 'react';
import { useContext } from 'react';
import styles from './page.module.css'
import { ThemeProvider } from "@mui/material/styles";

import theme from './Theme'
import Catalogs from './Catalogs'
import FooterBar from './components/FooterBar'
import Login from './Login'
import TitleBar from './components/TitleBar'
import { LoginCheck, LoginValidContext, DefaultLoginValid } from './checkLogin'

export default function Home() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState('');  
  const [url, setUrl] = useState('');
  const [remember, setRemember] = useState(false);  // TODO: lookup remember cookie: then set url & user if true
  const [loginValid, setLoginValid] = useState(DefaultLoginValid);

  function handle_login(url, user, password, remember) {
    setUser(user);
    setUrl(url);
    setRemember(remember);

    // Check parameters
    const validCheck = LoginCheck(url, user, password);

    setLoginValid(validCheck);
    if (loginValid.valid) {

      // Try to log user in
      //setLoggedIn(true);

      // If log in successful then...
        // Load catalogs
        if (remember == true) {
          // TODO: save remember, url, and user in cookie
        }
    }
  }

  const loginValidStates = loginValid;

  return (
    <main className={styles.main}>
      <ThemeProvider theme={theme}>
        <TitleBar/>
        {!loggedIn ? 
           <LoginValidContext.Provider value={loginValidStates}>
            <Login login_func={handle_login} prev_url={url} prev_user={user} prev_remember={remember} />
           </LoginValidContext.Provider>
         : <Catalogs />
        }
        <FooterBar/>
      </ThemeProvider>
    </main>
  )
}
