import urllib, urllib.request
import xmltodict
import argparse
import requests
from tqdm import tqdm
import os


def get_xml(id):
    url = "http://export.arxiv.org/api/query?id_list=" + id
    data = urllib.request.urlopen(url)
    xml = data.read().decode("utf-8")
    return xml


def parse_xml(xml):
    result = xmltodict.parse(xml)
    title = " ".join(result["feed"]["entry"]["title"].replace("\n", "").split())
    authors = result["feed"]["entry"]["author"]
    return title, authors


def format_output(title, authors, id):
    output = f"**{title}**."
    output += " _" + ", ".join(a["name"] for a in authors) + "_."
    output += f" [[{id}](https://arxiv.org/abs/{id})]"
    return output


def check_duplicate(output):
    with open("README.md", mode="r", encoding="utf-8") as file:
        readme_content = file.read()
    if output not in readme_content:
        return False
    else:
        return True


def download_pdf(args, id):
    if args.download:
        print(f"Downloading {id}.pdf")
        arxiv_url = f"https://arxiv.org/pdf/{id}.pdf"
        response = requests.get(arxiv_url, stream=True)

        if not os.path.exists(args.output_directory):
            os.makedirs(args.output_directory)

        output_file = os.path.join(args.output_directory, f"{id}.pdf")
        print(f"Saving to {output_file}")
        with open(output_file, "wb") as f:
            for chunk in tqdm(
                response.iter_content(chunk_size=1024),
            ):
                if chunk:
                    f.write(chunk)


def main(args):
    if args.url:
        id = args.url[args.url.rindex("/") + 1 :]
    elif args.arxiv_id:
        id = args.arxiv_id
    else:
        print("No valid input was provided. Please provide either --url or --arxiv-id.")
        return

    xml = get_xml(id)
    title, authors = parse_xml(xml)
    output = format_output(title, authors, id)

    if check_duplicate(output):
        print("The paper is already in the README.md file. Skipping...")
        return

    if not os.path.exists(args.write_file):
        print(f"Creating {args.write_file}")
        with open(args.write_file, mode="w", encoding="utf-8"):
            pass

    with open(args.write_file, mode="a", encoding="utf-8") as file:
        file.write("\n" + output + "\n")

    download_pdf(args, id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="arxiv url")
    group.add_argument("--arxiv-id", help="arXiv paper ID (e.g., '2107.12345')")

    parser.add_argument(
        "--write-file",
        default="README.md",
        help="File location for the file to save the paper to. Default is README.md",
    )

    parser.add_argument(
        "--download",
        action="store_true",
        help="Flag to indicate whether to download the paper or not",
    )

    parser.add_argument(
        "--output-directory",
        default=".",
        help="Output directory for the downloaded paper",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version="1.0.0"),
    )

    args = parser.parse_args()
    main(args)
