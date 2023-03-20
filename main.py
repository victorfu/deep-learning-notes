import urllib, urllib.request
import xmltodict
import argparse
import requests
from tqdm import tqdm
import os


def main(args):
    # If the user provided a URL, use the arXiv ID from that URL
    if args.url:
        id = args.url[args.url.rindex("/") + 1 :]
    # If the user provided an arXiv ID, use that
    elif args.arxiv_id:
        id = args.arxiv_id
    # If the user didn't provide anything, exit with an error message
    else:
        print("No valid input was provided. Please provide either --url or --arxiv-id.")
        return

    # Use the arXiv API to get the title and authors of the paper
    url = "http://export.arxiv.org/api/query?id_list=" + id
    data = urllib.request.urlopen(url)
    xml = data.read().decode("utf-8")
    result = xmltodict.parse(xml)
    title = " ".join(result["feed"]["entry"]["title"].replace("\n", "").split())
    authors = result["feed"]["entry"]["author"]

    # Format the title, authors, and URL into a Markdown citation
    output = f"**{title}**."
    output += " _" + ", ".join(a["name"] for a in authors) + "_."
    output += f" [[{id}](https://arxiv.org/abs/{id})]"
    print(output)

    # Check if the citation is already in the README and append it if not
    with open("README.md", mode="r") as file:
        readme_content = file.read()

    if output not in readme_content:
        # Append the citation to the README
        with open("README.md", mode="a") as file:
            file.write("\n" + output + "\n")
    else:
        print("The paper is already in the README.md file. Skipping...")

    # If the user provided the --download option, download the PDF
    if args.download:
        print(f"Downloading {id}.pdf")
        arxiv_url = f"https://arxiv.org/pdf/{id}.pdf"
        response = requests.get(arxiv_url, stream=True)

        # Create the output directory if it doesn't exist
        if not os.path.exists(args.output_directory):
            os.makedirs(args.output_directory)

        # Save the PDF to the specified output directory
        output_file = os.path.join(args.output_directory, f"{id}.pdf")
        print(f"Saving to {output_file}")
        with open(output_file, "wb") as f:
            for chunk in tqdm(
                response.iter_content(chunk_size=1024),
            ):
                if chunk:
                    f.write(chunk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Create a mutually exclusive group
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--url", help="arxiv url")
    group.add_argument("--arxiv-id", help="arXiv paper ID (e.g., '2107.12345')")

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
    print(args)
    main(args)
