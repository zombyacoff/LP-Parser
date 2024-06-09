# LP-Parser
`LP-Parser` is a Python script designed to parse login and password information from a list of websites. 
The script can handle different date formats and offset values for URLs, checking for the existence of these URLs and extracting login & password credentials. 
It's initially designed for [Telegraph](https://telegra.ph/), but you can try some other websites, so free your imagination.

## Features
- Configurable via `config.yml`
- Checks URL availability and extracts login credentials
- Supports offset values for URL generation
- Outputs results in a structured YAML file
- Async proccessing 

## Requirements
- [Python ^3.12](https://www.python.org/downloads/)
- Poetry

## Installation
1. Download the release and extract the zip.

2. Install poetry if you don't have it:
    ```bash
    pip install poetry
    ```

3. Go to the directory and install dependencies:
    ```bash
    cd LP-Parser
    poetry install
    ```

## Configuration
### Edit `config.yml` to configure the parser:
   - **offset**: Configure offset for URL generation (value must be an integer between 2 and 250, inclusive).
   - **release_date**: Specify if the release date filter should be used and which years to include.
   - **websites**: List of base URLs to parse.
   - **exceptions**: List of logins to exclude from parsing.
#### If you are some sort of dark wizard, who understands regex, we got some advanced settings for you!
   - **login_regex**: Change what will count as a login, by default we have email.
   - **password_regex**: Customize what will count as a password, by default we have word that contains digit.
### Example of config.yml
```yaml
offset:
  offset: true
  value: 2

release_date:
  release_date: true
  years:
  - 2024
  - 2023

websites:
- https://telegra.ph/steam

exceptions: 
- dmca@telegram.org

for_advanced_users:
  login_regex: \S+@\S+\.\S+
  password_regex: \S*\d\S*
```

## Usage
Run the script:
```bash
poetry run python main.py
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
  1. https://telegra.ph/steam-01-03
  2. https://telegra.ph/steam-01-03-2
```
