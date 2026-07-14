# Analytics Workspace Setup

## Project Description

This repository provides a standardized analytics development environment for data product teams.

## Setup

### Clone

git clone <repository-url>

### Create Virtual Environment

Windows

python -m venv venv

macOS/Linux

python3 -m venv venv

### Activate

Windows Git Bash

source venv/Scripts/activate

macOS/Linux

source venv/bin/activate

### Install

pip install -r requirements.txt

## Project Structure

data/raw - Raw datasets

data/processed - Processed datasets

notebooks - Jupyter notebooks

scripts - Python scripts

output - Generated outputs

## Notes

Copy .env.example to .env and replace the placeholder values with your own.

Do not commit the .env file.
