# AniPlay

A desktop app for managing and watching your local anime library.

## Features

*   **Scan & Organize:** Scan your local folders to automatically identify and organize your anime series.
*   **Metadata Fetching:** Automatically fetches metadata and covers from Anilist.
*   **Integrated Player:** Watch anime with the integrated MPV player.
*   **Search:** Quickly search through your anime library.
*   **Dark Theme:** A sleek dark theme for comfortable viewing.

## Dependencies

*   Python 3
*   PySide6
*   python-mpv
*   [mpv](https://mpv.io/installation/) (must be installed and accessible in your system's PATH)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/aniplay.git
    cd aniplay
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file may need to be created. See `src/app.py` for imports.)*

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