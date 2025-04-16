'use client'

/** @module utils */

/**
 * Returns the base portion of the URL
 * @function
 * @returns The base portion of the URL
 */
export function getServer() {
  let curUrl = '';
  if (typeof window !== "undefined") {
    curUrl = window.location.origin;
    curUrl = 'http://127.0.0.1:5000'  // TODO:
  }

  // modify as needed
  return curUrl;
}