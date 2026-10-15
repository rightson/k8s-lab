"""Render the isolated lesson manifest using an immutable local image tag."""
import argparse, re, sys
from pathlib import Path
import yaml

def render(image):
    if not re.fullmatch(r"k082-api:[0-9a-f]{12,64}", image):
        raise ValueError("Use k082-api:<content-derived-hex>; never latest or unbuilt")
    documents = list(yaml.safe_load_all(
        (Path(__file__).resolve().parents[1] / "manifests/app.yaml").read_text()))
    documents[1]["spec"]["template"]["spec"]["containers"][0]["image"] = image
    return yaml.safe_dump_all(documents, sort_keys=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    print(render(parser.parse_args().image), end="")

