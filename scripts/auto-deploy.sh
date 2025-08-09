#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Add all changes to git
cd /Users/offspring/Desktop/botitog

git add .

# Commit changes with a message
commit_message="Auto-deploy: $(date)"
git commit -m "$commit_message"

# Push changes to the main branch
git push origin main

# Print success message
echo "Deployment successful!"
