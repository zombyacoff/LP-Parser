# LP-Parser

## Overview
`LP-Parser` is a Python script designed to parse login and password information from a list of websites. 
The script can handle different date formats and offset values for URLs, checking for the existence of these URLs and extracting login & password credentials. 
It's initially designed for [Telegraph](https://telegra.ph/), but you can try some other websites, so free your imagination.

## Features
- Configurable via `settings.yml`
- Checks URL availability and extracts login credentials
- Supports offset values for URL generation
- Outputs results in a structured YAML file

## Requirements
- Python 3.x
- Required packages listed in `requirements.txt`

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/zombyacoff/LP-Parser.git
    cd LP-Parser
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration
1. Edit `settings.yml` to configure the parser:
    - **websites_list**: List of base URLs to parse.
    - **exceptions_list**: List of emails to exclude from parsing.
    - **offset**: Configure offset for URL generation.
    - **release_date**: Specify if the release date filter should be used and which years to include.
### Example of settings.yml
```yaml
offset:
  offset: true
  value: 3
release_date:
  release_date: true
  years:
    - 2022
    - 2023
websites_list:
  - "https://example.com/login"
exceptions_list:
  - "admin@example.com"
```

## Usage
Run the script using Python:
```bash
python lp_parser.py
```
## Output
The script generates an output file in the output folder with the parsed results, named based on the launch timestamp.
The final file will look something like this:
```yaml
login:
  1. jakeiscool2006
  2. somelogin
password:
  1. greatestpassword3
  2. somepassword7
url:
  1. https://website.net/gaming-02-13
  2. https://website.com/minecraft-06-19
```

