/**
 * Custom version updater for Python version.py file
 * Used by standard-version to update backend/app/version.py
 */

const stringifyPackage = require('standard-version/lib/updaters/types/json').writeFile

module.exports.readVersion = function (contents) {
  // Extract version from __version__ = "x.y.z"
  const versionMatch = contents.match(/__version__\s*=\s*["']([^"']+)["']/)
  return versionMatch ? versionMatch[1] : null
}

module.exports.writeVersion = function (contents, version) {
  const currentDate = new Date().toISOString().split('T')[0]

  // Update __version__
  contents = contents.replace(
    /__version__\s*=\s*["'][^"']+["']/,
    `__version__ = "${version}"`
  )

  // Update __version_info__
  const [major, minor, patch] = version.split('.').map(Number)
  contents = contents.replace(
    /__version_info__\s*=\s*\([^)]+\)/,
    `__version_info__ = (${major}, ${minor}, ${patch})`
  )

  // Update __build_date__
  contents = contents.replace(
    /__build_date__\s*=\s*["'][^"']*["']/,
    `__build_date__ = "${currentDate}"`
  )

  return contents
}
