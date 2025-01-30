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

function getLoginInfo() {
  if (!getURL()) {
    clearLoginInfo();
  }

  return {
    'url': getURL(),
    'user': getUsername(),
    'remember': getRemember()
  };
}

function setLoginInfo(url, username, remember) {
  setURL(url);
  setUsername(username);
  setRemember(remember);
}

function clearLoginInfo() {
  setURL('');
  setUsername('');
  setRemember(false);
}

function getURL() {
  return window.localStorage.getItem('login.url');
}

function getUsername() {
  return window.localStorage.getItem('login.user');
}

function getRemember() {
  return window.localStorage.getItem('login.remember');
}

function setURL(url) {
  window.localStorage.setItem('login.url', "" + url)
}

function setUsername(username) {
  window.localStorage.setItem('login.user', "" + username)
}

function setRemember(remember) {
  window.localStorage.setItem('login.remember', !!remember)
}

export default function Home() {
  const [savedLoginFetched, setSavedLoginFetched] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState('');
  const [url, setUrl] = useState('');
  const [remember, setRemember] = useState(false);  // TODO: lookup remember cookie: then set url & user if true
  const [loginValid, setLoginValid] = useState(DefaultLoginValid);

  const loginValidStates = loginValid;

  function handleLogin(url, user, password, remember) {
    setUser(user);
    setUrl(url);
    setRemember(remember);

    // Check parameters
    const validCheck = LoginCheck(url, user, password);

    setLoginValid(validCheck);
    if (validCheck.valid) {

      // Try to log user in
      setLoggedIn(true);

      // If log in successful then...
        if (remember == true) {
          setLoginInfo(url, user, remember);
        } else {
          clearLoginInfo();
        }
        // Load catalogs
    }
  }

  if (!savedLoginFetched && !loggedIn) {
    const loInfo = getLoginInfo();
    setSavedLoginFetched(true);
    if (loInfo != null) {
      setUrl(loInfo.url);
      setUser(loInfo.user);
      setRemember(!!loInfo.remember);
    }
  }

  return (
    <main className={styles.main}>
      <ThemeProvider theme={theme}>
        <TitleBar/>
        {!loggedIn ? 
           <LoginValidContext.Provider value={loginValidStates}>
            <Login prev_url={url} prev_user={user} prev_remember={remember} login_func={handleLogin} />
           </LoginValidContext.Provider>
         : <Catalogs />
        }
        <FooterBar/>
      </ThemeProvider>
    </main>
  )
}
