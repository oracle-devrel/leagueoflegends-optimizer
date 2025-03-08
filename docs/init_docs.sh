#!/bin/bash

# Initialize the documentation

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Initializing documentation${NC}"

# Check if Sphinx is installed
echo -e "\n${YELLOW}Checking Sphinx installation...${NC}"
if command -v sphinx-build &>/dev/null; then
    echo -e "${GREEN}Sphinx is installed.${NC}"
else
    echo -e "${YELLOW}Sphinx is not installed. Installing Sphinx...${NC}"
    pip install sphinx sphinx-rtd-theme myst-parser
    echo -e "${GREEN}Sphinx installed successfully.${NC}"
fi

# Create static directory if it doesn't exist
echo -e "\n${YELLOW}Creating static directory...${NC}"
mkdir -p source/_static
echo -e "${GREEN}Static directory created.${NC}"

# Create a placeholder logo
echo -e "\n${YELLOW}Creating placeholder logo...${NC}"
if [ ! -f "source/_static/logo.png" ]; then
    # Use a simple command to create a placeholder image
    # This is just a placeholder, you should replace it with your actual logo
    echo "This is a placeholder for the logo. Replace with your actual logo." > source/_static/logo.txt
    echo -e "${GREEN}Placeholder logo created. Please replace it with your actual logo.${NC}"
else
    echo -e "${GREEN}Logo already exists.${NC}"
fi

# Create a placeholder favicon
echo -e "\n${YELLOW}Creating placeholder favicon...${NC}"
if [ ! -f "source/_static/favicon.ico" ]; then
    # Use a simple command to create a placeholder favicon
    # This is just a placeholder, you should replace it with your actual favicon
    echo "This is a placeholder for the favicon. Replace with your actual favicon." > source/_static/favicon.txt
    echo -e "${GREEN}Placeholder favicon created. Please replace it with your actual favicon.${NC}"
else
    echo -e "${GREEN}Favicon already exists.${NC}"
fi

# Build the documentation
echo -e "\n${YELLOW}Building documentation...${NC}"
make html
echo -e "${GREEN}Documentation built successfully.${NC}"

echo -e "\n${GREEN}Documentation initialized successfully!${NC}"
echo -e "You can now view the documentation by opening ${YELLOW}build/html/index.html${NC} in your browser."
echo -e "To publish the documentation to ReadTheDocs, follow the instructions in the ${YELLOW}development.rst${NC} file." 