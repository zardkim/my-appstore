/**
 * Version information for MyApp Store Frontend
 *
 * This file is automatically updated by the release process.
 * Do not edit manually.
 */

export const version = "1.3.1"
export const versionInfo = {
  major: 1,
  minor: 3,
  patch: 1
}

export const buildInfo = {
  buildDate: "2026-01-24",
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
