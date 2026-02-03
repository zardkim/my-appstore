/**
 * Version information for MyApp Store Frontend
 *
 * This file is automatically updated by the release process.
 * Do not edit manually.
 */

export const version = "1.5.6"
export const versionInfo = {
  major: 1,
  minor: 5,
  patch: 6
}

export const buildInfo = {
  buildDate: "2026-02-03",
  gitCommit: ""  // Set during build if needed
}

export function getVersion() {
  return version
}

export function getVersionInfo() {
  return {
    version: version,
    ...versionInfo,
    ...buildInfo
  }
}

export default {
  version,
  versionInfo,
  buildInfo,
  getVersion,
  getVersionInfo
}
