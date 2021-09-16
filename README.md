# pubchem2excel tool to extract pub chem molecules, images, to html 

## Limitation

1. not tested thoroughly
2. excel has no image

## How to use?

0. Clone repo

    ```bash
    git clone https://github.com/liongkj/pubchem2excel.git && cd pubchem2excel
    code .
    ```

1. Edit input.txt
One element per line

2. Install requirements

    ```bash
    pip install -r requirements.txt
    ```

3. Run script

    ```bash
    python main.py
    ```

4. Output format: HTML (with image), excel
