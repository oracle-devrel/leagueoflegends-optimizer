#!/bin/bash
# Copyright (c) 2021 Oracle and/or its affiliates.
# Unset current variables and reset TNS_ADMIN and LD_LIBRARY_PATH.
unset TNS_ADMIN
unset LD_LIBRARY_PATH

export LD_LIBRARY_PATH=/home/$USER/git/devrel-esports/pkg/instantclient_21_1:$LD_LIBRARY_PATH
export TNS_ADMIN=/home/$USER/git/devrel-esports/pkg/instantclient_21_1/network/admin

source ~/.bashrc

# League of Legends Optimizer Setup Script
# This script helps set up the League of Legends Optimizer project

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}League of Legends Optimizer Setup${NC}"
echo "This script will help you set up the League of Legends Optimizer project."

# Check if Python 3.8+ is installed
echo -e "\n${YELLOW}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        echo -e "${GREEN}Python $PYTHON_VERSION is installed.${NC}"
    else
        echo -e "${RED}Python 3.8 or higher is required. Found $PYTHON_VERSION.${NC}"
        exit 1
    fi
else
    echo -e "${RED}Python 3 is not installed.${NC}"
    exit 1
fi

# Check if Poetry is installed
echo -e "\n${YELLOW}Checking Poetry installation...${NC}"
if command -v poetry &>/dev/null; then
    echo -e "${GREEN}Poetry is installed.${NC}"
else
    echo -e "${YELLOW}Poetry is not installed. Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    echo -e "${GREEN}Poetry installed successfully.${NC}"
fi

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
poetry install
echo -e "${GREEN}Dependencies installed successfully.${NC}"

# Create config.yaml if it doesn't exist
echo -e "\n${YELLOW}Setting up configuration...${NC}"
if [ ! -f "config.yaml" ]; then
    echo -e "${YELLOW}Creating config.yaml...${NC}"
    cat > config.yaml << EOF
# League of Legends Optimizer Configuration

riot_api:
  key: REPLACE_WITH_YOUR_API_KEY

database:
  type: sqlite

message_queue:
  host: localhost
  port: 5672
  username: league
  password: league
  queue_name: live_client
  heartbeat: 600
  blocked_connection_timeout: 300

live_client:
  base_url: https://127.0.0.1:2999/liveclientdata
  request_interval: 30

model:
  save_path: models/trained
EOF
    echo -e "${GREEN}Created config.yaml. Please edit it to add your Riot API key.${NC}"
else
    echo -e "${GREEN}config.yaml already exists.${NC}"
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs models/trained
echo -e "${GREEN}Directories created.${NC}"

# Activate the virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
poetry shell &

echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo -e "To get started, run the following commands:"
echo -e "  1. Edit config.yaml to add your Riot API key"
echo -e "  2. Run 'poetry shell' to activate the virtual environment"
echo -e "  3. Run 'leagueoptimizer visualizer' to start the web visualization"
echo -e "\nFor more information, see the README.md file."