# AnyFlip PDF Toolkit

A comprehensive toolkit to download books from AnyFlip as PDFs and aggressively compress existing PDFs. Built with Python and CustomTkinter for a modern, dark-mode user interface.

## Features

### 1. AnyFlip Downloader
*   **Lossless & Compressed Downloads**: Automatically fetches high-quality images from AnyFlip URLs and compiles them into a PDF. Choose between `Lossless`, `High`, `Medium`, and `Low` quality directly during the download.
*   **Intelligent Routing**: Automatically falls back to multiple CDNs, formats (e.g., `.webp`, `.jpg`), and resolutions (`large`, `mobile`) to bypass 403 Forbidden errors if a specific format is unavailable.
*   **Size Estimation**: Press `Check Size` to parse the `config.js` of the book and estimate the total MB footprint based on your selected compression level *before* starting the download.

### 2. PDF Compressor
*   **Standalone Compression**: Choose any image-based PDF on your machine and dramatically reduce its size to make it suitable for email or web sharing.
*   **PyMuPDF Engine**: Uses `fitz` (PyMuPDF) to render PDF pages losslessly, downsamples the DPI, compresses via Pillow's JPEG optimization algorithms, and reconstructs the PDF on the fly. 
*   *Note: Text-based PDFs will be rasterized to images, losing text-searchability, as this tool is primarily optimized for image-based flipbooks.*

## Installation

1.  Clone this repository or download the source code.
2.  Install the required dependencies via pip:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Simply run the main python script to launch the GUI:
```bash
python anyflip_downloader.py
```
