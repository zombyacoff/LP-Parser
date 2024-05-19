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
- Async proccessing 

## Requirements
- [Python 3.x](https://www.python.org/downloads/)
- Required packages listed in `requirements.txt`

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/zombyacoff/LP-Parser.git
    ```

2. Install dependencies:
    ```bash
    cd LP-Parser
    pip install -r requirements.txt
    ```

## Configuration
### Edit `settings.yml` to configure the parser:
   - **websites_list**: List of base URLs to parse.
   - **exceptions_list**: List of emails to exclude from parsing.
   - **offset**: Configure offset for URL generation.
   - **release_date**: Specify if the release date filter should be used and which years to include.
#### If you are some sort of dark wizard, who understands regex, we got some advanced settings for you!
   - **login_regex**: Change what will count as a login, by default we have email.
   - **password_regex**: Customize what will count as a password, by default we have password that contains digit.
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
for_advanced_users:
  login_regex: "\S+@\S+\.\S+"
  password_regex: "\S*\d\S*"
```

## Usage
### Windows 
- Double-click the `run_lp_parser.bat` file to run the program. The following file consists this code:
   
    ```batch
    @echo off
    python lp_parser.py
    pause
    ```
    
### Unix-based Systems (Linux, macOS)
1. Lookup a `run_lp_parser.sh` file with the following content:
    ```bash
    #!/bin/bash
    python3 lp_parser.py
    ```
    
2. Make the script executable:
   ```bash
   chmod +x run_lp_parser.sh
   ```
   
3. Run the script:
   ```bash
   ./run_lp_parser.sh
   ```
   
## Output
The script generates an output file in the output folder with the parsed results, named based on the launch timestamp.
The final file will look something like this:
```yaml
login:
  1. jakeiscool2006@mail.com
  2. somelogin@email.com
password:
  1. greatestpassword3
  2. somepassword7
url:
  1. https://example.com/login-01-03
  2. https://example.com/login-01-07
```

