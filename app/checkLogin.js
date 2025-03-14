'use client'

/** @module checkLogin */

import { createContext } from 'react';

// Default login values state
export const DefaultLoginValid = {'url': true, 'user': true, 'password': true, 'valid': false};
// Context for login validity
export const LoginValidContext = createContext(DefaultLoginValid);

/**
 * Check the URL for correctness
 * @function
 * @param {string} url The URL to check
 * @return {boolean} Returns true if the URL matches the valid format
 */
export function LoginCheckURL(url) {
  const url_expression = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
  const url_regex = new RegExp(url_expression);
  return url.match(url_regex) != null;
}

/**
 * Checks that the user name is valid
 * @function
 * @param {string} user The username to check
 * @returns {boolean} Returns true if the user name appears to be valid
 */
export function LoginCheckUser(user) {
  return user != '';
}

/**
 * Checks that the password is valid
 * @function
 * @param {string} password The password to check
 * @returns {boolean} Returns true if the password appears to be valid
 */
export function LoginCheckPassword(password) {
  return password != '';
}

/**
 * Checks that the login credentials appear to be valid
 * @function
 * @param {string} url The URL to check
 * @param {string} user The username to check
 * @param {string} password The password to check
 * @returns {object} Returns the validity of each parameter, and overall validity
 */
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
