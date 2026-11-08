"""Download the AWS Price List Bulk API offer files for this project.

Run it from the folder that holds this file:

    uv run python download_data.py

That downloads eight current price lists and three small index files into a
folder named data next to this script. About 643 MB in total.

    uv run python download_data.py --check

downloads nothing. It asks Amazon's server for the size of every file and
prints whether the size still matches the table in the data overview document.
Run this first if you want to know what you are about to pull down.

    uv run python download_data.py --small

skips the two big EC2 files and gets only the nine small ones, about 57 MB.
Useful on a slow connection, or when you only need the Bedrock, S3, Lambda,
RDS and SageMaker price sheets.

If this script fails. Some networks and some servers block scripted
requests. If any file prints FAILED, an HTTP error, or "no answer", do not
debug it. Download the same eleven files yourself in the browser, using
Route A in section 4 of the data overview document, rename each one to the
name shown there, and put them in the data folder next to this script. The
two routes produce exactly the same eleven files.

A note on the word "current" in these addresses. Amazon republishes a price
list whenever any price in it changes, so the file behind
.../current/... is whatever Amazon published most recently. The fingerprints
below were recorded on 5 September 2026. If this script prints
"checksum differs", Amazon has published a newer version since then. That is
normal and it is not an error. The version stamp is on line 4 of every file
you download.

Standard library only. Python 3.11.
"""

import hashlib
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

CHUNK = 1024 * 256

# Each entry: local file name, URL, expected size in bytes, sha256, group.
# Group "small" is always downloaded. Group "big" is skipped with --small.
# Sizes and hashes were read from the server on 5 September 2026.
#
# The address pattern is BASE + "/{serviceCode}/{version}/{regionCode}/index.csv".
# Leave out the region code and you get the all-region file for that service,
# which for EC2 was 5.96 GB on 5 September 2026. That is why the two EC2
# entries and the RDS entry below name a region and the other five do not:
# the all-region EC2 and RDS files are far too big to take whole, while the
# SageMaker, S3, Lambda and Bedrock offers are small enough that the
# all-region file is the convenient one.
FILES = [
    # The three index files. Small, and they tell you what else exists.
    ("offer_index.json",
     BASE + "/index.json", 89686,
     "d933ad313f6851115ba3b2c6f1afb994e14ebee3cdd6f3b4fd3a95a780067f8c", "small"),
    ("ec2_version_index.json",
     BASE + "/AmazonEC2/index.json", 28596,
     "f02333e9649636643cbb1ce59d6dcfaee9a052e3f3296c170c789eb2760d7f09", "small"),
    ("ec2_region_index.json",
     BASE + "/AmazonEC2/current/region_index.json", 18705,
     "fb0828354b43adef86c7ed06044513a0bc3219904fb12514985ce5cb4d168c97", "small"),
    # The six small price lists.
    ("rds_us-east-1.csv",
     BASE + "/AmazonRDS/current/us-east-1/index.csv", 18071150,
     "25e0f200d7c889346fd71ff2de248fc8e1c5e8113cd07a21e09ef32ff47e78fe", "small"),
    ("sagemaker_all.csv",
     BASE + "/AmazonSageMaker/current/index.csv", 23183589,
     "f8f87f917ba86242a06453716bd53ed9d620ae5a52b82c92d3a0d19aaff91c0b", "small"),
    ("s3_all.csv",
     BASE + "/AmazonS3/current/index.csv", 4281817,
     "2a5ac166cdfc9d846179c720d501cdda133dbe283b99765a713f12eaa4100c04", "small"),
    ("lambda_all.csv",
     BASE + "/AWSLambda/current/index.csv", 4377341,
     "824217a2042a1efb1a05c325ddc61f2d9596a3932db956f15bc064c90eccc8b9", "small"),
    ("bedrock_foundation_models.csv",
     BASE + "/AmazonBedrockFoundationModels/current/index.csv", 2093036,
     "5e5db5eaa7188d2c7db4f4697337573a70839e0948551efb35d9a4b9904ef3bd", "small"),
    ("bedrock_service_all.csv",
     BASE + "/AmazonBedrock/current/index.csv", 5345568,
     "03a74cb1b657fbd43beeb36ac17317111bc203c212a3d0ceda9b9565e84af82d", "small"),
    # The two big EC2 regional price lists.
    ("ec2_us-east-1.csv",
     BASE + "/AmazonEC2/current/us-east-1/index.csv", 303506818,
     "fad41bf668635019d8e5b8dbe6436324e1a4c28715bd201b5b4e1319fcc359c5", "big"),
    ("ec2_eu-west-1.csv",
     BASE + "/AmazonEC2/current/eu-west-1/index.csv", 282126325,
     "fab0186b573ad22d97f09d1b37e03b1648d2244e8bd62086a3e8254c20eedf42", "big"),
]


def open_url(url, method):
    """Open a URL with a browser User-Agent header."""
    request = urllib.request.Request(url, method=method)
    request.add_header("User-Agent", USER_AGENT)
    return urllib.request.urlopen(request, timeout=180)


def remote_size(url):
    """Return the size the server reports for a URL, or None."""
    try:
        response = open_url(url, "HEAD")
        length = response.headers.get("Content-Length")
        response.close()
        if length is None:
            return None
        return int(length)
    except Exception as error:
        print("  could not reach the server: " + str(error))
        print("  If this keeps happening, the network is probably blocking "
              "scripted requests. Use Route A in section 4 of the data "
              "overview document and download the files in the browser.")
        return None


def download_one(url, target, expected_bytes, expected_hash):
    """Download one file, printing name, size in MB and elapsed seconds."""
    label = target.name
    if target.exists() and target.stat().st_size == expected_bytes:
        print(label + ": already downloaded, " +
              str(round(expected_bytes / 1000000.0, 1)) + " MB, skipped")
        return True

    started = time.time()
    hasher = hashlib.sha256()
    written = 0
    try:
        response = open_url(url, "GET")
        with open(str(target), "wb") as handle:
            while True:
                block = response.read(CHUNK)
                if not block:
                    break
                handle.write(block)
                hasher.update(block)
                written = written + len(block)
        response.close()
    except Exception as error:
        print(label + ": FAILED, " + str(error))
        print("  Some networks and servers block scripted requests. Download "
              "this file in the browser instead, using Route A in section 4 "
              "of the data overview document, rename it to " + label +
              " and put it in the data folder.")
        return False

    elapsed = round(time.time() - started, 1)
    print(label + ": " + str(round(written / 1000000.0, 1)) + " MB in " +
          str(elapsed) + " seconds")
    if written != expected_bytes:
        print("  size differs (the publisher may have updated the file): got " +
              str(written) + " bytes, expected " + str(expected_bytes))
    if hasher.hexdigest() == expected_hash:
        print("  checksum ok")
    else:
        print("  checksum differs (the publisher may have updated the file)")
    return True


def run_check(wanted):
    """Ask the server for every size and compare with the expected size."""
    print("Checking file sizes on Amazon's server. Nothing is downloaded.")
    print("")
    total = 0
    problems = 0
    for name, url, expected_bytes, expected_hash, group in wanted:
        size = remote_size(url)
        if size is None:
            print(name + ": no answer")
            problems = problems + 1
            continue
        total = total + size
        if size == expected_bytes:
            print(name + ": ok, " + str(round(size / 1000000.0, 1)) + " MB")
        else:
            print(name + ": size differs (the publisher may have updated the "
                  "file): server says " + str(size) + " bytes, expected " +
                  str(expected_bytes))
            problems = problems + 1
    print("")
    print("Checked " + str(len(wanted)) + " files, " +
          str(round(total / 1000000.0, 1)) + " MB in total, " +
          str(problems) + " differences from the data overview document.")


def main():
    small_only = "--small" in sys.argv
    check_only = "--check" in sys.argv

    here = Path(__file__).resolve().parent
    data_dir = here / "data"
    data_dir.mkdir(exist_ok=True)

    wanted = []
    for entry in FILES:
        if entry[4] == "small" or not small_only:
            wanted.append(entry)

    if check_only:
        run_check(wanted)
        return

    print("Saving into: " + str(data_dir))
    if small_only:
        print("Getting the nine small files only. Drop --small for the two "
              "EC2 regional price lists as well.")
    print("")

    started = time.time()
    done = 0
    failed = 0
    for name, url, expected_bytes, expected_hash, group in wanted:
        if download_one(url, data_dir / name, expected_bytes, expected_hash):
            done = done + 1
        else:
            failed = failed + 1

    minutes = round((time.time() - started) / 60.0, 1)
    print("")
    print("Done: " + str(done) + " files in place, " + str(failed) +
          " failed, " + str(minutes) + " minutes.")
    if failed:
        print("")
        print("Some files did not arrive. Download those in the browser "
              "instead: Route A in section 4 of the data overview document "
              "lists all eleven links and the name to save each one as. Put "
              "them in the data folder and every snippet still works.")


if __name__ == "__main__":
    main()
