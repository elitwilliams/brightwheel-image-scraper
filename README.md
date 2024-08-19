# Brightwheel Scraper

This Python script automates the process of downloading photos from Brightwheel, an education management platform. It logs into your Brightwheel account, navigates to a specified student's profile, and downloads all photos within a given date range.

## Features

- Automatic login to Brightwheel
- Selection of a specific student's profile
- Date range filtering for photos
- Automatic scrolling and loading of all available photos
- Downloading and organizing photos by date

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher
- pip (Python package manager)
- Google Chrome browser installed

## Installation

1. Clone this repository or download the script.

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

   Note: You may want to do this in a virtual environment.

3. Create a `config.yml` file in the same directory as the script with the following structure:

   ```yaml
   bwuser: "your_brightwheel_username"
   bwpass: "your_brightwheel_password"
   bwsignin: "https://schools.mybrightwheel.com/sign-in"
   bwlist: "https://schools.mybrightwheel.com/students"
   startdate: "MM/DD/YYYY"
   enddate: "MM/DD/YYYY"
   ```

   Replace the values with your actual Brightwheel credentials and desired date range.

## Usage

Run the script from the command line:

```
python brightwheel_scraper.py
```

If you want to select a specific student by their number in the list, use the `-n` or `--student-number` option:

```
python brightwheel_scraper.py -n 1
```

This will select the first student in the list. If you don't use this option, you'll be prompted to select a student interactively.

## Important Notes

- **Two-Factor Authentication (2FA)**: After logging in, you will need to enter a 2FA code sent to your email within 30 seconds. Be prepared to access your email quickly after starting the script.

- **Login Attempts**: If you attempt to log in too many times in quick succession, your account may be temporarily locked out. If this happens, wait for a short period before trying again.

- This script uses Selenium with undetected_chromedriver to automate browser interactions. Make sure you have the latest version of Chrome installed.
- The script includes random waits between actions to mimic human behavior and avoid being flagged as a bot.
- Be respectful of Brightwheel's systems and terms of service when using this script.

## Output

The script will create a `pics` directory in the same location as the script. Inside this directory, it will save all downloaded photos with filenames in the format:

```
YYYY-MM-DD-0001.jpg
```

Where `YYYY-MM-DD` is the date of the photo, and the number at the end is a sequential counter for photos from the same day.

## Logging

The script logs its actions to both the console and a file named `scraper.log`. Check this file for detailed information about the script's execution and any errors that may occur.

## Troubleshooting

If you encounter any issues:

1. Check the `scraper.log` file for error messages.
2. Ensure your `config.yml` file is correctly formatted and contains valid credentials.
3. Make sure you have the latest version of Chrome installed.
4. Check that all required Python packages are installed correctly.
5. If you're consistently getting locked out, try increasing the wait times in the script.

## Disclaimer

This script is for personal use only. Make sure you comply with Brightwheel's terms of service when using this script. The authors are not responsible for any misuse or any violations of Brightwheel's terms of service.
