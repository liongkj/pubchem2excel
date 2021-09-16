import pandas as pd
import requests
import json

from PIL import Image
from IPython.core.display import display, HTML
import io

from io import BytesIO
from tqdm import tqdm
import os
import urllib

import base64


def main():
    dir_base = os.getcwd()
    file = open("input.txt", "r")
    lines = file.readlines()
    lines.sort()
    # nonempty_lines = [line.strip("\n") for line in file]
    line_count = len(lines)
    print(line_count)
    file.close()
    notfound = ""
    with open("input.txt", "r") as file1:
        df_prop_col = pd.DataFrame(
            columns=[
                "name",
                "structure",
                "IUPAC Name",
                "Molecular Formula",
                "Molecular Weight",
                "InChI",
                "Log P",
                "Hydrogen Bond Acceptor",
                "Hydrogen Bond Donor",
            ]
        )
        for index, d in enumerate(tqdm(file1, total=line_count)):
            slugify = urllib.parse.quote(d.strip().lower())
            response = requests.get(
                f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{slugify}/json"
            )
            # print
            if response.status_code == 200:
                res = response.json()
                # print(res)
                comp = res["PC_Compounds"][0]
                # print(comp.keys())
                cid = comp["id"]["id"]["cid"]
                props = comp["props"]
                prop_keys = [
                    "IUPAC Name",
                    "Molecular Formula",
                    "Molecular Weight",
                    "InChI",
                    "Log P",
                    "Hydrogen Bond Acceptor",
                    "Hydrogen Bond Donor",
                ]
                prop_dic = {}
                for p in prop_keys:
                    for pr in props:
                        if (
                            (p == "IUPAC Name")
                            and pr["urn"]["label"] == p
                            and pr["urn"]["name"] == "Systematic"
                        ):
                            prop_dic[pr["urn"]["label"]] = pr["value"]["sval"]
                        elif (
                            (p == "Log P")
                            and pr["urn"]["label"] == p
                            and "name" in pr["urn"]
                            and pr["urn"]["name"] == "XLogP3"
                        ):
                            prop_dic[pr["urn"]["label"]] = pr["value"]["fval"]
                        elif (p.startswith("Hydrogen")) and pr["urn"][
                            "label"
                        ] == "Count":
                            prop_dic[pr["urn"]["name"]] = pr["value"]["ival"]
                        elif p == pr["urn"]["label"]:
                            prop_dic[pr["urn"]["label"]] = pr["value"].values()
                # prop_tup = [()]
                # prop_list.append(prop_tup)

                structure = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{slugify}/PNG"
                # df_prop_col = pd.DataFrame.from_records(prop_tup,columns=prop_keys)
                image_name = f"{slugify}.jpg"
                local_path_thumb = os.path.join(dir_base, "output", "img", image_name)
                if not os.path.isfile(local_path_thumb):
                    urllib.request.urlretrieve(structure, local_path_thumb)

                df_prop_col.loc[index] = [
                    d.strip(),
                    get_thumbnail(local_path_thumb),
                    prop_dic.get("IUPAC Name"),
                    prop_dic.get("Molecular Formula"),
                    prop_dic.get("Molecular Weight"),
                    prop_dic.get("InChI"),
                    prop_dic.get("Log P"),
                    prop_dic.get("Hydrogen Bond Acceptor"),
                    prop_dic.get("Hydrogen Bond Donor"),
                ]

            elif response.status_code == 404:
                print(f"{d.strip()} not found!")
                notfound += f"{d.strip()}\n"
                # Code here will react to failed requests
        print("Saving to excel and HTML")
        pd.set_option("display.max_colwidth", None)
        df_prop_col.to_excel("./output/index.xlsx", index=False)
        df_prop_col.index = df_prop_col.index + 1
        df_prop_col.style.set_properties(**{"text-align": "left"})
        html = df_prop_col.to_html(
            escape=False, formatters={"structure": image_formatter}
        )
        nt_found = open("./output/notfound.txt", "w")
        nt_found.write(notfound)
        nt_found.close()
        text_file = open("./output/index.html", "w")
        text_file.write(html)
        text_file.close()


def get_thumbnail(path):
    # path = (
    #     "\\\\?\\" + path
    # )  # This "\\\\?\\" is used to prevent problems with long Windows paths
    i = Image.open(path)
    return i


def image_base64(im):
    if isinstance(im, str):
        im = get_thumbnail(im)
    with BytesIO() as buffer:
        im.convert("RGB").save(buffer, "jpeg")
        return base64.b64encode(buffer.getvalue()).decode()


def image_formatter(im):
    return f'<img src="data:image/jpeg;base64,{image_base64(im)}">'


if __name__ == "__main__":
    main()
