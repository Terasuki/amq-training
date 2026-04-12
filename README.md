# AMQ Utils

AMQ Utils is a local Flask/Dash web app that provides several utilities:

- Local database songs played
- Live song history of the last song played
- Minimal dashboard of songs played

## Usage instructions

AMQ Utils requires of a external Tampermonkey script to receive data from AMQ. 

### Installing the script

Make sure Tampermonkey is installed in your browser, then click [here](https://github.com/Terasuki/amq-training/raw/refs/heads/main/downloader.user.js).

Tampermonkey should automatically pop up for installation, otherwise manually copy and paste into a new script in Tampermonkey's library.

### Installing the server

You will need a valid Python installation. The project is tested on Python 3.14.3.

Install dependencies,

`pip install -r requirements.txt`.

Then start the server by running

`python app.py`.
