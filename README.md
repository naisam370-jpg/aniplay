# AniPlay

A desktop app for managing and watching your local anime library.

## Features

*   **Library Scanning:** Scan your local folders to automatically identify and organize your anime series based on file names.
*   **Metadata Fetching:** Automatically fetches metadata (like descriptions and genres) and covers from the Anilist API.
*   **Integrated Player:** Watch anime with an integrated MPV player interface.
*   **Detailed Views:** See detailed information for each series, including sub-series and episodes.
*   **Database:** Uses a local SQLite database to store your library information.
*   **Search:** Quickly search through your anime library.
*   **Customizable Settings:** Set your library path and other preferences.
*   **Dark Theme:** A sleek dark theme for comfortable viewing.

## Requirements

### Software

*   **Python 3**
*   **[mpv](https://mpv.io/installation/)**: The `mpv` player must be installed and accessible in your system's PATH.

### Python Dependencies

All required Python packages are listed in the `requirements.txt` file and can be installed with pip. Key dependencies include:

*   **PySide6:** For the user interface.
*   **Requests:** For fetching metadata from the Anilist API.
*   **rapidfuzz:** For fuzzy string matching in the search functionality.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/naisam370-jpg/aniplay.git
    cd aniplay
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install mpv:**
    Follow the instructions for your operating system on the [mpv website](https://mpv.io/installation/).

## Usage

1.  Run the application:
    ```bash
    python src/app.py
    ```
2.  Go to the **Settings** view.
3.  Set your anime library path.
4.  Click **"Scan Library"** to start the scanning and metadata fetching process.
5.  Once the scan is complete, your anime will appear in the **Library** view.

## Screenshots

*(Coming soon)*

## License

This project is licensed under the terms of the LICENSE file.
