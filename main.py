import pandas as pd
import requests
import json

from IPython.core.display import display,HTML
import io
from tqdm import tqdm


def main():
    file = open("input.txt", "r")
    nonempty_lines = [line.strip("\n") for line in file ]
    line_count = len(nonempty_lines)
    file.close()
    with open('input.txt', 'r') as file1:
        df_prop_col = pd.DataFrame(columns=['name', 'structure', "IUPAC Name","Molecular Formula","Molecular Weight", "InChI","Log P","Hydrogen Bond Acceptor","Hydrogen Bond Donor"])
        for index, d in enumerate(tqdm(file1, total=line_count)):
            response = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{d.strip().lower()}/json")
            # print
            if (response.status_code == 200):
                res = response.json()
                # print(res)
                comp =res['PC_Compounds'][0]
                # print(comp.keys())
                cid = comp["id"]['id']['cid']
                props = comp['props']
                prop_keys = ["IUPAC Name","Molecular Formula","Molecular Weight", "InChI", "Log P","Hydrogen Bond Acceptor","Hydrogen Bond Donor"]
                prop_dic= {}
                for p in prop_keys:
                    for pr in props:
                        if(p=="IUPAC Name") and pr["urn"]["label"] ==p and pr["urn"]["name"] == "Systematic":
                            prop_dic[pr["urn"]["label"]]=pr["value"]["sval"]
                        elif(p=="Log P") and pr["urn"]["label"]==p and 'name' in pr["urn"] and pr["urn"]["name"] == "XLogP3":
                            prop_dic[pr["urn"]["label"]]=pr["value"]["fval"]
                        elif(p.startswith("Hydrogen")) and pr["urn"]["label"]=="Count" :
                            prop_dic[pr["urn"]["name"]] = pr["value"]["ival"]
                        elif(p==pr["urn"]["label"]):
                            prop_dic[pr["urn"]["label"]] = pr["value"].values()
                # prop_tup = [()]
                # prop_list.append(prop_tup)
                
                structure = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{d.strip()}/PNG'
                # df_prop_col = pd.DataFrame.from_records(prop_tup,columns=prop_keys)
                

                image_cols = ['structure']  #<- define which columns will be used to convert to html

                # Create the dictionariy to be passed as formatters
                format_dict = {}
                for image_col in image_cols:
                    format_dict[image_col] = path_to_image_html

                # res2 = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/assaysummary/csv")
                # if (res2.status_code == 200):
                #     df = pd.read_csv(io.StringIO(res2.content.decode('utf-8')))
                #     print(df["Bioassay Type"])
                #     # print(df)
                df_prop_col.loc[index] = [d.strip(), structure, prop_dic["IUPAC Name"], prop_dic["Molecular Formula"], prop_dic["Molecular Weight"], prop_dic["InChI"],prop_dic["Log P"],prop_dic["Hydrogen Bond Acceptor"],prop_dic["Hydrogen Bond Donor"] ]
            
            elif (response.status_code == 404):
                print("Result not found!")
                # Code here will react to failed requests
        print("Saving to excel and HTML")
        pd.set_option('display.max_colwidth', None)
        df_prop_col.to_excel('./output/index.xlsx', index=False)
        df_prop_col.index = df_prop_col.index + 1
        df_prop_col.style.set_properties(**{'text-align': 'left'})
        html = df_prop_col.to_html(escape=False ,formatters=format_dict)
        text_file = open("./output/index.html", "w")
        text_file.write(html)
        text_file.close()



def path_to_image_html(path):
    return '<img src="'+ path + '" width="250" >'

if __name__ == "__main__":
    main()
