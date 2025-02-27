import sys
import os
import csv
import email
import logging
import shutil
from datetime import datetime
from email import policy
from email.parser import BytesParser
import hashlib

script_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(script_dir, "input")
logs_dir = os.path.join(script_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

timestamp = datetime.now().strftime("logs_%d_%m_%Y_%H_%M_%S.txt")
log_file = os.path.join(logs_dir, timestamp)
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

def compute_hash(file_path):
    hash_func = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def remove_attachments(msg, target_names, count, removed):
    if msg.is_multipart():
        new_payload = []
        for part in msg.get_payload():
            filename = part.get_filename()
            cd = part.get("Content-Disposition", "")
            if cd and "attachment" in cd.lower() and filename in target_names:
                count[0] += 1
                removed.add(filename)
                continue
            else:
                new_payload.append(remove_attachments(part, target_names, count, removed))
        msg.set_payload(new_payload)
    return msg

def process_eml_file(input_path, output_path, target_attachment_names):
    try:
        with open(input_path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)
    except Exception as e:
        logging.error(f"Error reading {input_path}: {e}")
        return

    count = [0]
    removed_names = set()
    clean_msg = remove_attachments(msg, target_attachment_names, count, removed_names)

    missing = target_attachment_names - removed_names
    if missing:
        for att in missing:
            logging.error(f"Expected attachment '{att}' not found in {os.path.basename(input_path)}.")

    if count[0] == 0:
        try:
            shutil.copy2(input_path, output_path)
        except Exception as e:
            logging.error(f"Error copying file {input_path} to {output_path}: {e}")
            return
    else:
        try:
            with open(output_path, "wb") as f:
                f.write(clean_msg.as_bytes())
        except Exception as e:
            logging.error(f"Error writing cleaned file {output_path}: {e}")
            return

    logging.info(f"Deleted {count[0]} attachments from {os.path.basename(input_path)}")

    try:
        input_hash = compute_hash(input_path)
        output_hash = compute_hash(output_path)
        if input_hash != output_hash:
            logging.info(f"Hash mismatched for {os.path.basename(input_path)}: Input hash: {input_hash}, Output hash: {output_hash}. Files are different.")
        else:
            logging.error(f"Hash match for {os.path.basename(input_path)}: {input_hash}. Files are the same!")
    except Exception as e:
        logging.error(f"Error computing file hash for {input_path} or {output_path}: {e}")

def main():
    if len(sys.argv) < 2:
        error_msg = "Usage: python remove_attachment.py input.csv [-rem2]"
        print(error_msg)
        logging.error(error_msg)
        sys.exit(1)

    csv_file = os.path.join(script_dir, sys.argv[1])
    # Vérifier si l'option -rem2 est présente dans les arguments
    rem2 = "-rem2" in sys.argv[2:]
    logging.info(f"Starting CSV processing: {csv_file} | Remove 2 characters: {rem2}")

    files_to_remove = {}
    try:
        with open(csv_file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            for row in reader:
                if len(row) < 2:
                    logging.warning(f"Skipping row with less than 2 columns: {row}")
                    continue
                eml_filename = row[0].strip()
                attachment_name = row[1].strip()
                # Si l'option -rem2 est activée, on retire les deux premiers caractères
                if rem2:
                    if len(attachment_name) >= 2:
                        attachment_name = attachment_name[2:]
                    else:
                        attachment_name = ""
                if not eml_filename:
                    logging.warning(f"Skipping row with empty filename: {row}")
                    continue
                files_to_remove.setdefault(eml_filename, set()).add(attachment_name)
    except Exception as e:
        logging.error(f"Error reading CSV file {csv_file}: {e}")
        sys.exit(1)

    logging.info(f"CSV processing complete. {len(files_to_remove)} files to process.")

    output_dir = os.path.join(script_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    for eml_filename, attachment_names in files_to_remove.items():
        input_eml_path = os.path.join(input_dir, eml_filename)
        if not os.path.exists(input_eml_path):
            logging.error(f"Input file not found: {input_eml_path}")
            continue

        base, ext = os.path.splitext(eml_filename)
        output_eml_path = os.path.join(output_dir, base + "_clean" + ext)
        os.makedirs(os.path.dirname(output_eml_path), exist_ok=True)

        logging.info(f"Processing {eml_filename} to remove attachments: {attachment_names}")
        process_eml_file(input_eml_path, output_eml_path, attachment_names)

if __name__ == "__main__":
    main()
