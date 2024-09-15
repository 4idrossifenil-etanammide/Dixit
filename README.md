# DIXIT PROJECT

This repository contains the code used to create, fine tune and test the Dixit bot.

The directory structure is the following:

- **analyze**:  The folder contains all the code used to analyze the data produced during games both against GPT and humans. It also contains the analysis made for the games with GPT.

    - **data**: contains the game analysis againts GPT
    - **create_data.py**: 
        ```console
        usage: create_data.py [-h] -src SRC_FOLDER -dst DST_FOLDER

        optional arguments:
        -h, --help            show this help message and exit
        -src SRC_FOLDER, --src_folder SRC_FOLDER
                                Specify the directory from which we want to take the data
        -dst DST_FOLDER, --dst_folder DST_FOLDER
                                Specify the directory to which we want to save the data
        ```
        To use the file, place yourself inside ```analyze/``` and use the mandatory flags to select the source data folder and the destination data folder.
        The program will recreate the dir structure of the source data folder, and it will take the .txt games and generate the correspondent .xlsx files (the games in an excel format). 
    - **analyze_data.py**:
        ```console
        usage: analyze_data.py [-h] -df DATA_FOLDER [-hu]

        optional arguments:
        -h, --help            show this help message and exit
        -df DATA_FOLDER, --data_folder DATA_FOLDER
                                Specify the directory from which we want to take the data
        -hu, --human          Specify that the game to be analyzed are from humans
        ```
        To use the file, place yourself inside ```analyze/``` and use the mandatory flag to select the source data folder. The analysis results are gonna be placed inside the same folders from which the data are taken.
        The program will take the .xlsx files and generate some statistics for them (e.g. Percentage of votes when the player was a narrator) in another .xlsx file, named ```*_analysis.xlsx```.
        Other than the single game analysis, also a summarization for all the games inside the folder will be produced. This recap will be contained inside ```summarize.xlsx/``` and it will show the average statistics between GPT vs bot or humans vs bot.

        > **_NOTE:_**  Remember to specify the -hu flag if the games are from humans, otherwise the summarization will break!

- **cards**: The folder contains three set of cards

    - **original_cards**: contains the cards from the original edition of Dixit. This set was used during fine tuning.
    - **online_cards**: contains the cards found online at this link: https://github.com/jminuscula/dixit-online/tree/master/cards. They were used for testing
    - **odissey_cards**: contains the cards from the Odissey edition of Dixit. This set was used during real life games against humans


        
