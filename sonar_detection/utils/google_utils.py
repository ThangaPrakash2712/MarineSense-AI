# Google utils: https://cloud.google.com/storage/docs/reference/libraries

import os
import platform
import subprocess
import time
from pathlib import Path

import requests
import torch


def gsutil_getsize(url=''):
    s = subprocess.check_output(f'gsutil du {url}', shell=True).decode('utf-8')
    return eval(s.split(' ')[0]) if len(s) else 0


def attempt_download(file, repo='WongKinYiu/yolov7'):
    """
    Attempt to download file if it does not exist.
    FIXED: If weights already exist locally, skip download.
    """
    file = Path(str(file).strip().replace("'", ""))

    # ✅ FIX: Skip download if file exists
    if file.exists():
        print(f"Using local weights: {file}")
        return

    print(f"{file} not found. Attempting download...")

    try:
        response = requests.get(
            f'https://api.github.com/repos/{repo}/releases/latest'
        ).json()

        assets = [x['name'] for x in response.get('assets', [])]
        tag = response.get('tag_name', 'latest')

    except Exception:
        # fallback assets list
        assets = [
            'yolov7.pt',
            'yolov7-tiny.pt',
            'yolov7x.pt',
            'yolov7-d6.pt',
            'yolov7-e6.pt',
            'yolov7-e6e.pt',
            'yolov7-w6.pt'
        ]
        tag = 'latest'

    name = file.name

    if name in assets:
        try:
            url = f'https://github.com/{repo}/releases/download/{tag}/{name}'
            print(f"Downloading {url} to {file}...")
            torch.hub.download_url_to_file(url, file)

            if not file.exists() or file.stat().st_size < 1E6:
                raise Exception("Download incomplete")

        except Exception as e:
            print(f"Download failed: {e}")
            if file.exists():
                file.unlink()
            print("Please download the weights manually.")


def gdrive_download(id='', file='tmp.zip'):
    t = time.time()
    file = Path(file)
    cookie = Path('cookie')

    print(f'Downloading https://drive.google.com/uc?export=download&id={id} as {file}...', end='')

    file.unlink(missing_ok=True)
    cookie.unlink(missing_ok=True)

    out = "NUL" if platform.system() == "Windows" else "/dev/null"

    os.system(f'curl -c ./cookie -s -L "drive.google.com/uc?export=download&id={id}" > {out}')

    if os.path.exists('cookie'):
        s = f'curl -Lb ./cookie "drive.google.com/uc?export=download&confirm={get_token()}&id={id}" -o {file}'
    else:
        s = f'curl -s -L -o {file} "drive.google.com/uc?export=download&id={id}"'

    r = os.system(s)
    cookie.unlink(missing_ok=True)

    if r != 0:
        file.unlink(missing_ok=True)
        print('Download error')
        return r

    if file.suffix == '.zip':
        print('unzipping... ', end='')
        os.system(f'unzip -q {file}')
        file.unlink()

    print(f'Done ({time.time() - t:.1f}s)')
    return r


def get_token(cookie="./cookie"):
    with open(cookie) as f:
        for line in f:
            if "download" in line:
                return line.split()[-1]
    return ""