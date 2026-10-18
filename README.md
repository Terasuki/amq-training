# AMQ Utils

AMQ Utils is a local web app (a Flask server with a React UI) that provides several utilities:

- Local database songs played
- Live song history of the last song played
- Minimal dashboard of songs played

## Usage instructions

AMQ Utils requires of a external Tampermonkey script to receive data from AMQ.

### Installing the script

Make sure Tampermonkey is installed in your browser, then click [here](https://github.com/Terasuki/amq-training/raw/refs/heads/main/downloader.user.js).

Tampermonkey should automatically pop up for installation, otherwise manually copy and paste into a new script in Tampermonkey's library.

### Running the server

You will need [uv](https://docs.astral.sh/uv/) and Node.js to build the UI. uv downloads and manages the Python interpreter itself (Python 3.15, pinned in `.python-version`). The project is tested on Python 3.15 and Node.js 24.

Install dependencies,

`uv sync`.

Build the UI,

`cd frontend && npm install && npm run build`.

Then, from the repository root,

`uv run app.py`,

which starts a Flask development server (receives the data from the userscript and serves the UI).

The dashboard itself can be accessed on the localhost link in the terminal.

_Warning: this opens your computer to potential bad actors if they know which port you are hosting the server. I am not responsible for any damage this may incur._

### Working on the UI

The UI lives in `frontend/` (React + Vite). With `uv run app.py` running, start Vite's dev server,

`cd frontend && npm run dev`,

and open the link it prints.
