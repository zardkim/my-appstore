"""
Version information for MyApp Store Backend

This file is automatically updated by the release process.
Do not edit manually.
"""

__version__ = "1.5.6"
__version_info__ = (1, 5, 6)

# Build information (optional, can be set during build process)
__build_date__ = "2026-02-03"
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
