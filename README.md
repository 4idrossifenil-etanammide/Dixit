# DIXIT PROJECT

This repository contains the code used to create, fine tune and test the Dixit bot.


Examples of captions extracted by the Dixit agent:

<p align="center">
  <img src="cards/odissey_cards/9.jpg" alt="Image 1" width="25%" style="margin-right: 30px;" />
  <img src="cards/odissey_cards/5.jpg" alt="Image 2" width="25%" style="margin-left: 30px;" />
</p>
<p align="center">
  <i>"Ethereal whimsy in geometric harmony"</i> &emsp;&emsp;&emsp; <i>"Melancholic harmony in nature's embrace"</i>
</p>

---

To obtain:  
1. The dataset used for fine tuning the models  
2. The online data on which the preliminary experiments were performed
3. The COCO dataset
4. The weights for the trained models  

Open the following link: https://drive.google.com/drive/folders/1qgqw7JFqq3zDcVvqbmL9RlGp1tv2RwEO?usp=drive_link

To use the files in this repo take the content inside ```training_results/``` and paste it in the local folder ```weights/```. 

> **_NOTE:_** If you want to reproduce the results obtained using the notebook inside ```models_and_finetuning/``` you will have to copy the content of the drive folder and place inside your Drive, in a folder named ```Dixit/```

---

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

- **cards**: The folder contains three set of cards. Each card has a number associated with it.

    - **original_cards**: contains the cards from the original edition of Dixit. This set was used during fine tuning.
    - **online_cards**: contains the cards found online at this link: https://github.com/jminuscula/dixit-online/tree/master/cards. They were used for testing.
    - **odissey_cards**: contains the cards from the Odissey edition of Dixit. This set was used during real life games against humans. (The CLIP tests proves that those are the hardest cards for the model)

- **game**: The folder contains the code used to create a terminal based game of Dixit played using the Odissey edition cards. To play it, place yourself inside the folder and run the main.py file.
    ```console
        usage: main.py [-h] [-np N_PLAYERS] [-p] [--gpt_players GPT_PLAYERS] [--points_to_win POINTS_TO_WIN] [--print_cards]

        optional arguments:
        -h, --help            show this help message and exit
        -np N_PLAYERS, --n_players N_PLAYERS
                                Specify the number of players
        -p, --play            Let the player play against the bots
        --gpt_players GPT_PLAYERS
                                Specify number of GPT players
        --points_to_win POINTS_TO_WIN
                                Specify the number of points to win
        --print_cards         Print the card in the hands of the players for each round
    ```
    The card are represented and printed using their name: a number (the numeration can be found inside the cards/odissey_cards folder). You can play against the bots and GPT bots by specifying the flag -p. Note that when specifying the number of players, by default they will be all Dixit agents. By adding gpt players or a human player, the number of Dixit agents decreases so that the total number of players remain the same:

    Example:  
    &emsp; ```python main.py -np 5 -p --gpt_players 2```  
    &emsp; The above command let the player play against 2 GPT players and 2 Dixit agents (5 total players minus 1 human player minus 2 GPT players)

    In general, the cards in the hands of the players are not gonna be printed, so if you want to visualize them, add the flag --print_cards. The default amount of points required to win is 30 (as it is in the actual game), but if you want to modify it to test a shorter version of the game you are free to do so by specifying the correspondent flag.

    > **_NOTE:_**  If you want to play against GPT, you have to insert the API key inside the game.py file!

- **models_and_finetuning**: The folder contains a Jupyter Notebook used to define and fine tune all the models here used, plus some additional failed experiments. For further details, read the report or look at the explanatory cells in the notebook.

- **real_life_playing**: The folder contains the notebook used for real life experiments along with the results and analysis.  
    - **human_games**: Folder containing the human games performed in the format of a .txt file
    - **human results**: Folder containing the results and analysis of the human games in an .xlsx format
    - **bot.ipynb**: The notebook used for human testing

- **testing_and_captions_generation**: The folder contains two notebooks used for testing the CLIP and BLIP fine tuned models. The BLIP testing notebook was originally used to extract the descriptive captions from the cards, before the rephrasing (refer to the report about the dataset creation).
    - **test_blip.ipynb**: Notebook used to visualize the captions produced with the fine tuned BLIP model. Said captions can be also saved to a file if specified, and if the fine tuned weights for the model are not provided, it will simply output descriptive captions.
    - **test_clip.ipynb**: Notebook used to test the performances of CLIP under different circumstances (e.g. BLIP vs CLIP, fine tuned BLIP vs CLIP, fine tuned BLIP vs fine tuned CLIP, etc...). In this file the models are tested over the three set of cards available, and because of this it can be clearly seen that the hardest cards for the models are the ones from the Odissey edition.

---