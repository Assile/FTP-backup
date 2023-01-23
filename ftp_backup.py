import argparse
import ftplib
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

SIZE_NAMES = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]


def connect(host, user, password):
    connection = ftplib.FTP(host)
    connection.login(user, password)
    return connection


def size_to_human_readable(size):
    current_size = size
    exponent = 0
    while current_size >= 1024:
        exponent += 1
        current_size = size / 1024**exponent

    return round(current_size), SIZE_NAMES[exponent]


def download_all(connection, file_paths, save_location):
    connection.sendcmd("TYPE I")
    longest_string = max([len(str(s)) for s in file_paths])
    index_max_width = len(str(len(file_paths)))

    timer_total = datetime.now()
    for index, one_file in enumerate(file_paths, 1):
        timer = datetime.now()
        human_readable_size, human_readable_size_abbreviation = size_to_human_readable(
            connection.size(str(one_file.as_posix()))
        )
        print(
            f"{index:>{index_max_width}}/{len(file_paths)} {str(one_file):<{longest_string}} | {human_readable_size:>4} {human_readable_size_abbreviation:<3}",
            end="",
        )
        sys.stdout.flush()
        (save_location / one_file).parent.mkdir(parents=True, exist_ok=True)
        with open(save_location / one_file, "wb") as f:
            connection.retrbinary(f"RETR {one_file.as_posix()}", f.write)
        print(f" | {datetime.now() - timer} | {datetime.now() - timer_total}")


def get_all_file_paths(connection, current_path=None):
    if current_path is None:
        current_path = Path(".")

    file_names = []
    connection.retrlines("NLST", file_names.append)
    ls_data = []
    connection.retrlines("LIST", lambda x: ls_data.append(x.split()))
    ls_types = [datum[0] for datum in ls_data]
    file_sizes_bytes = [int(datum[4]) for datum in ls_data]

    file_paths = []
    for ls_type, file_size_bytes, file_name in zip(
        ls_types, file_sizes_bytes, file_names
    ):
        if ls_type.startswith("d"):
            connection.cwd(file_name)
            file_paths.extend(get_all_file_paths(connection, current_path / file_name))
            connection.cwd("..")
        else:
            file_paths.append(current_path / file_name)
            print(f"{len(file_paths)} Found: {current_path / file_name}")

    return file_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backup the contents of an FTP server."
    )
    parser.add_argument(
        "target_location",
        type=str,
        help="The location where the files will be downloaded to.",
    )
    parser.add_argument(
        "--time_stamp",
        "-t",
        action="store_true",
        help="Add a timestamped folder to the target location to download the files to.",
    )
    args = parser.parse_args()

    timer = datetime.now()
    load_dotenv()

    with connect(
        os.getenv("FTP_HOST"), os.getenv("FTP_USER"), os.getenv("FTP_PASSWORD")
    ) as connection:
        save_location = Path(args.target_location)
        if args.time_stamp:
            save_location /= f"{datetime.now():%Y-%m-%d %H.%M.%S}"
        save_location.mkdir(parents=True, exist_ok=True)

        file_paths = get_all_file_paths(connection)

        download_all(connection, sorted(file_paths), save_location)
    print(f"Total time taken: {datetime.now() - timer}")
