import urllib, urllib.request
import xmltodict
import argparse
import requests
from tqdm import tqdm


def main(args):
    id = args.url[args.url.rindex("/") + 1 :]
    url = "http://export.arxiv.org/api/query?id_list=" + id
    data = urllib.request.urlopen(url)
    xml = data.read().decode("utf-8")
    result = xmltodict.parse(xml)
    title = " ".join(result["feed"]["entry"]["title"].replace("\n", "").split())
    authors = result["feed"]["entry"]["author"]

    output = f"**{title}**."
    output += " _" + ", ".join(a["name"] for a in authors) + "_."
    output += f" [[{id}](https://arxiv.org/abs/{id})]"
    print(output)

    with open("README.md", mode="a") as file:
        file.write("\n" + output + "\n")

    if args.download:
        print(f"Downloading {id}.pdf")
        arxiv_url = f"https://arxiv.org/pdf/{id}.pdf"
        response = requests.get(arxiv_url, stream=True)
        with open(f"{id}.pdf", "wb") as f:
            for chunk in tqdm(
                response.iter_content(chunk_size=1024),
            ):
                if chunk:
                    f.write(chunk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--url", help="arxiv url", required=True)
    parser.add_argument(
        "--download",
        action="store_true",
        help="Flag to indicate whether to download the paper or not",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version="1.0.0"),
    )

    args = parser.parse_args()
    main(args)
