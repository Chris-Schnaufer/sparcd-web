'use client'

import { createContext } from 'react';

export const DefaultLoginValid = {'url': true, 'user': true, 'password': true, 'valid': false};
export const LoginValidContext = createContext(DefaultLoginValid);

export function LoginCheckURL(url) {
  const url_expression = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
  const url_regex = new RegExp(url_expression);
  return url.match(url_regex) != null;
}

export function LoginCheckUser(user) {
  return user != '';
}

export function LoginCheckPassword(password) {
  return password != '';
}

export function LoginCheck(url, user, password) {
  const urlValid = LoginCheckURL(url);
  const userValid = LoginCheckUser(user);
  const passwordValid = LoginCheckPassword(password);

  return {
    'url': urlValid,
    'user': userValid,
    'password': passwordValid,
    'valid': urlValid && userValid && passwordValid
  };
}
