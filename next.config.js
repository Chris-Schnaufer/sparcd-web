/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
 
  // Optional: Change links `/me` -> `/me/` and emit `/me.html` -> `/me/index.html`
  // trailingSlash: true,
 
  // Optional: Prevent automatic `/me` -> `/me/`, instead preserve `href`
  // skipTrailingSlashRedirect: true,
 
  // Optional: Change the output directory `out` -> `dist`
  // distDir: 'dist',

  // https://github.com/vercel/next.js/issues/21079
  // Remove this workaround whenever the issue is fixed
  //images: {
  //  unoptimized: true,
  //},

}

module.exports = nextConfig
