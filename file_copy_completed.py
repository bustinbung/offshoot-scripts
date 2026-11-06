# OffShoot File Copy Completed script
# Author: Justin Jung
# Date: 2026-11/06

import sys
import json
import traceback
import subprocess
from pathlib import Path, PurePath
from typing import TypedDict, cast

# Loose typing created from JSON object returned by OffShoot
class FileCopyCompleted(TypedDict):
    FileCopyCompleted_id: str
    FileCopyCompleted_state: str
    FileCopyCompleted_verification_mode: str
    FileCopyCompleted_transferLogJSONPath: Path
    FileCopyCompleted_destinationPath: Path
    FileCopyCompleted_startedAt: str
    FileCopyCompleted_sourcePaths: list[str]
    FileCopyCompleted_sourceInfo: dict[str, str]
    FileCopyCompleted_duration: str
    FileCopyCompleted_presetName: str
    FileCopyCompleted_bytesCopied: str

## FUNCTIONS ##

def create_foolcat_report(event: FileCopyCompleted):
    transfer_destination_path = Path(event["FileCopyCompleted_destinationPath"])
    if not transfer_destination_path.exists():
        raise Exception("Destination path not found at " + str(transfer_destination_path))

    # .resolve() collapses dot notation to absolute path
    report_folder_path = Path(transfer_destination_path, "../../../../../03-Misc/00-Reports").resolve()
    report_folder_path.mkdir(exist_ok=True)
    if not report_folder_path.exists():
        raise Exception("Report folder not found at " + str(report_folder_path))
    print("Report destination: " + str(report_folder_path))

    source_info = event["FileCopyCompleted_sourceInfo"]
    source_date = source_info["Date"]
    report_destination_path = Path(report_folder_path, source_date, "FoolCat_Reports")
    report_destination_path.mkdir(exist_ok=True, parents=True)
    if not report_destination_path.exists():
        raise Exception("Dated report folder not found at " + str(report_destination_path))
    print("Creating FoolCat report at " + str(report_destination_path))

    # I believe this implementation makes this script NOT cross-platform, as Windows uses a different command. Should be any easy fix.
    _ = subprocess.run(
        ["open", str("foolcat://create?source=" + str(transfer_destination_path) + "&destination=" + str(report_destination_path))],
        check=True
    )

    print("Started FoolCat job!")

def copy_transfer_log(event: FileCopyCompleted):
    transfer_json_path = PurePath(event["FileCopyCompleted_transferLogJSONPath"])
    transfer_log_path = Path(transfer_json_path.parent, transfer_json_path.stem + ".txt")
    if not transfer_log_path.exists():
        raise Exception("Transfer log not found at " + str(transfer_log_path))
    print("Found report at " + str(transfer_log_path))

    transfer_destination_path = Path(event["FileCopyCompleted_destinationPath"])
    if not transfer_destination_path.exists():
        raise Exception("Transfer destination not found at " + str(transfer_destination_path))

    report_folder_path = Path(transfer_destination_path, "../../../../../03-Misc/00-Reports").resolve()
    report_folder_path.mkdir(exist_ok=True)
    if not report_folder_path.exists():
        raise Exception("Report folder not found at " + str(report_folder_path))
    print("Report copy destination: " + str(report_folder_path))

    source_info = event["FileCopyCompleted_sourceInfo"]
    source_date = source_info["Date"]
    report_destination_path = Path(report_folder_path, source_date, "Transfer_Logs")
    report_destination_path.mkdir(exist_ok=True, parents=True)
    if not report_destination_path.exists():
        raise Exception("Dated report folder not found at " + str(report_destination_path))

    print("Copying report to " + str(report_destination_path))
    result_path = transfer_log_path.copy_into(report_destination_path)
    if not result_path.exists():
        raise Exception("Copy failed!")

    print("Copy success!")

def create_proxy_job(event: FileCopyCompleted):
    transfer_destination_path = Path(event["FileCopyCompleted_destinationPath"])
    if not transfer_destination_path.exists():
        raise Exception("Transfer destination not found at " + str(transfer_destination_path))
    print("Creating proxies for " + str(transfer_destination_path))

    proxy_folder_path = Path(transfer_destination_path, "../../../01-Proxy").resolve()
    proxy_folder_path.mkdir(exist_ok=True)
    if not proxy_folder_path.exists():
        raise Exception("Proxy parent folder not found at " + str(transfer_destination_path))

    proxy_destination_path = Path(proxy_folder_path, transfer_destination_path.parts[-2], transfer_destination_path.parts[-1])
    proxy_destination_path.mkdir(exist_ok=True, parents=True)
    if not proxy_destination_path.exists():
        raise Exception("Proxy destination folder not found at " + str(transfer_destination_path))
    print("Creating proxies in " + str(proxy_destination_path))

    editready_preset = Path("/Users/justin/Library/Application Support/EditReady/ProResProxy-2499SL3SG3C.erpreset")

    _ = subprocess.run(
        ["open", str("editready://transcode?sourcePath=" + str(transfer_destination_path) + "&preset=" + str(editready_preset) + "&destinationPath=" + str(proxy_destination_path))],
        check=True
    )

    print("Started proxy job!")


## SCRIPT START ##

print("Starting script...")

event = cast(FileCopyCompleted, json.loads(sys.argv[1]))
print("Loaded event JSON")

if (event["FileCopyCompleted_state"] != "Success"):
    sys.exit("File copy state not success!")
print("File copy succeeded, continuing...")

try:
    create_foolcat_report(event)
except Exception:
    print(traceback.format_exc())

try:
    copy_transfer_log(event)
except Exception:
    print(traceback.format_exc())

try:
    create_proxy_job(event)
except Exception:
    print(traceback.format_exc())

print("Script success!")
