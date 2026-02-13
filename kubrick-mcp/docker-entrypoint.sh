#!/bin/bash
set -e

# Create shared_media directory if it doesn't exist
mkdir -p /app/shared_media

# Fix ownership to pixeltable user (UID 1000)
chown -R pixeltable:pixeltable /app/shared_media

# Switch to pixeltable user and execute the CMD
exec gosu pixeltable "$@"
