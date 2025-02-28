'use client'

export function getServer() {
  let curUrl = '';
  if (typeof window !== "undefined") {
    curUrl = window.location.origin;
  }

  // modify as needed
  return curUrl;
}