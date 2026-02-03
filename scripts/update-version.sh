#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get version from argument or latest git tag
if [ -z "$1" ]; then
  # Get latest git tag
  VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')
  if [ -z "$VERSION" ]; then
    echo -e "${RED}Error: No version provided and no git tags found${NC}"
    echo "Usage: $0 <version>"
    echo "Example: $0 1.5.3"
    exit 1
  fi
  echo -e "${YELLOW}Using version from latest git tag: ${VERSION}${NC}"
else
  VERSION=$1
  echo -e "${YELLOW}Using provided version: ${VERSION}${NC}"
fi

# Validate version format (semantic versioning)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo -e "${RED}Error: Invalid version format. Must be X.Y.Z (e.g., 1.5.3)${NC}"
  exit 1
fi

# Extract version components
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"
BUILD_DATE=$(date +%Y-%m-%d)

echo -e "${GREEN}Updating version to ${VERSION}...${NC}"

# 1. Update frontend/package.json
echo "Updating frontend/package.json..."
PACKAGE_JSON="frontend/package.json"
if [ -f "$PACKAGE_JSON" ]; then
  # Use sed to update version in package.json
  sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"${VERSION}\"/" "$PACKAGE_JSON"
  echo -e "${GREEN}✓ Updated ${PACKAGE_JSON}${NC}"
else
  echo -e "${RED}✗ ${PACKAGE_JSON} not found${NC}"
fi

# 2. Update backend/app/version.py
echo "Updating backend/app/version.py..."
VERSION_PY="backend/app/version.py"
if [ -f "$VERSION_PY" ]; then
  cat > "$VERSION_PY" << EOF
"""
Version information for MyApp Store Backend

This file is automatically updated by the release process.
Do not edit manually.
"""

__version__ = "${VERSION}"
__version_info__ = (${MAJOR}, ${MINOR}, ${PATCH})

# Build information (optional, can be set during build process)
__build_date__ = "${BUILD_DATE}"
__git_commit__ = ""  # Set during build if needed

def get_version() -> str:
    """Get the version string"""
    return __version__

def get_version_info() -> dict:
    """Get detailed version information"""
    return {
        "version": __version__,
        "major": __version_info__[0],
        "minor": __version_info__[1],
        "patch": __version_info__[2],
        "build_date": __build_date__,
        "git_commit": __git_commit__
    }
EOF
  echo -e "${GREEN}✓ Updated ${VERSION_PY}${NC}"
else
  echo -e "${RED}✗ ${VERSION_PY} not found${NC}"
fi

# 3. Update frontend/src/version.js
echo "Updating frontend/src/version.js..."
VERSION_JS="frontend/src/version.js"
if [ -f "$VERSION_JS" ]; then
  cat > "$VERSION_JS" << EOF
/**
 * Version information for MyApp Store Frontend
 *
 * This file is automatically updated by the release process.
 * Do not edit manually.
 */

export const version = "${VERSION}"
export const versionInfo = {
  major: ${MAJOR},
  minor: ${MINOR},
  patch: ${PATCH}
}

export const buildInfo = {
  buildDate: "${BUILD_DATE}",
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
EOF
  echo -e "${GREEN}✓ Updated ${VERSION_JS}${NC}"
else
  echo -e "${RED}✗ ${VERSION_JS} not found${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Version updated successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Version: ${GREEN}${VERSION}${NC}"
echo -e "Build Date: ${GREEN}${BUILD_DATE}${NC}"
echo ""
echo "Updated files:"
echo "  - frontend/package.json"
echo "  - backend/app/version.py"
echo "  - frontend/src/version.js"
