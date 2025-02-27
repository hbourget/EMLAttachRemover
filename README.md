# EMLAttachRemover

![MIT License](https://img.shields.io/badge/License-MIT-black)
![Python Script](https://img.shields.io/badge/3.0+-Python-blue)

This tool processes `.eml` files to remove specified attachments based on a CSV file. It preservers file metadata and integrity.

## Features

- **.eml Parsing:** Recursively removes specified attachments from email files.
- **CSV:** Uses a semicolon-delimited CSV file to map `.eml` filenames to attachment filenames.
- **Hash verification:** Computes and compares SHA-256 hashes before and after processing.
- **Logging:** Detailed, timestamped logs track actions and errors, output in .txt file

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hbourget/EMLAttachRemover
   cd EMLAttachRemover
   ```
2. **Prepare directories:**
   - Create an `input` directory in the project root and add your `.eml` files.
   - The script will automatically create `logs` and `outputs` directories.

3. **Prepare the CSV file:**
   - Create a CSV file (e.g., `input.csv`) in the project root.
   - Format each row as: `eml_filename;attachment_filename`

## Usage

Run the script with the CSV file as an argument:
```bash
python remove_attachment.py input.csv
```

- Processed files will be saved in the `outputs` directory with a `_clean` suffix.
- Logs are written in the `logs` directory with a timestamp in the filename.

## License

This project is licensed under the [MIT License](./LICENSE).
