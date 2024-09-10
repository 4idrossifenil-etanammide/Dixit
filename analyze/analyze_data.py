import os
import argparse
from argparse import Namespace
import pandas as pd

def argument_parsing() -> Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("-df", "--data_folder", type=str, help="Specify the directory from which we want to take the data", required=True)

    return parser.parse_args()

def calculate_narrator_votes(votes_df):
    narrator_stats = {}
    rounds = votes_df['Round'].unique()
    
    for rnd in rounds:
        round_data = votes_df[votes_df['Round'] == rnd]
        narrator = round_data['Narrator'].iloc[0]
        total_players = round_data['Player'].nunique() - 1 
        
        votes_for_narrator_card = round_data[round_data['Player'] == narrator]["Voted By"].item()
        votes_count = -1
        if votes_for_narrator_card == "no one":
            votes_count = 0
        else:
            votes_count = len(votes_for_narrator_card.split(","))

        if narrator not in narrator_stats:
            narrator_stats[narrator] = {'voted_by_all': 0, 'voted_by_none': 0, 'voted_by_someone':0, 'total_rounds': 0}
        
        narrator_stats[narrator]['total_rounds'] += 1
        if votes_count == total_players:
            narrator_stats[narrator]['voted_by_all'] += 1
        elif votes_count == 0:
            narrator_stats[narrator]['voted_by_none'] += 1
        else:
            narrator_stats[narrator]['voted_by_someone'] += 1
    
    for narrator in narrator_stats:
        total_rounds = narrator_stats[narrator]['total_rounds']
        narrator_stats[narrator]['percent_voted_by_all'] = (narrator_stats[narrator]['voted_by_all'] / total_rounds) * 100
        narrator_stats[narrator]['percent_voted_by_none'] = (narrator_stats[narrator]['voted_by_none'] / total_rounds) * 100
        narrator_stats[narrator]['percent_voted_by_someone'] = (narrator_stats[narrator]['voted_by_someone'] / total_rounds) * 100
    
    return pd.DataFrame.from_dict(narrator_stats, orient='index')

def calculate_votes_when_not_narrator(votes_df):
    player_stats = {}
    for player in votes_df['Player'].unique():
        player_votes = votes_df[(votes_df['Player'] == player) & (votes_df['Narrator'] != player)]
        total_rounds = player_votes.shape[0]
        voted_rounds = player_votes[~player_votes['Voted By'].str.contains("no one", na=False)].shape[0]
        
        player_stats[player] = {
            'total_rounds': total_rounds,
            'voted_rounds': voted_rounds,
            'percent_voted_when_not_narrator': (voted_rounds / total_rounds) * 100 if total_rounds > 0 else 0
        }
    
    return pd.DataFrame.from_dict(player_stats, orient='index')

def calculate_correct_votes_for_narrator(votes_df):
    correct_vote_stats = {}
    for player in votes_df['Player'].unique():
        player_votes = votes_df[votes_df['Voted By'].str.contains(player, na=False)]
        total_votes = player_votes.shape[0]
        correct_votes = player_votes[player_votes["Player"] == player_votes["Narrator"]].shape[0]
        
        correct_vote_stats[player] = {
            'total_votes': total_votes,
            'correct_votes': correct_votes,
            'percent_correct_votes_for_narrator': (correct_votes / total_votes) * 100 if total_votes > 0 else 0
        }
    
    return pd.DataFrame.from_dict(correct_vote_stats, orient='index')

def create_analysis(path_to_excel: str, path_to_save: str):
    narrations_df = pd.read_excel(path_to_excel, sheet_name='Narrations')
    votes_df = pd.read_excel(path_to_excel, sheet_name='Votes')

    votes_df = votes_df.merge(narrations_df, on='Round', how='left', suffixes=('', '_narrator'))

    narrator_vote_stats = calculate_narrator_votes(votes_df)
    votes_when_not_narrator_stats = calculate_votes_when_not_narrator(votes_df)
    correct_votes_stats = calculate_correct_votes_for_narrator(votes_df)

    with pd.ExcelWriter(path_to_save) as writer:
        narrator_vote_stats.to_excel(writer, sheet_name='Narrator Votes Stats', index=True)
        votes_when_not_narrator_stats.to_excel(writer, sheet_name='Votes When Not Narrator', index=True)
        correct_votes_stats.to_excel(writer, sheet_name='Correct Votes Stats', index=True)

def compute_combined_averages(file_list, sheet_name, value_cols):
    combined_data = pd.DataFrame()

    for file_path in file_list:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        player_type_col = df.columns[0] 
        combined_data = pd.concat([combined_data, df], ignore_index=True)

    gpt_players = combined_data[combined_data[player_type_col].str.match(r'^GPT Bot', case=False, na=False)]
    bot_players = combined_data[combined_data[player_type_col].str.match(r'^Bot(?!.*GPT)', case=False, na=False)]

    gpt_averages = gpt_players[value_cols].mean().to_frame(name='GPT Average')
    bot_averages = bot_players[value_cols].mean().to_frame(name='Bot Average')

    combined_averages = pd.concat([gpt_averages, bot_averages], axis=1)
    return combined_averages

def compute_winners_stats(original_files):
    tot_gpt_winners = 0
    tot_bot_winners = 0

    for file_path in original_files:
        df = pd.read_excel(file_path, sheet_name = "Winners")
        gpt_players = df[df["Player"].str.match(r'^GPT Bot', case=False, na=False)]
        bot_players = df[df["Player"].str.match(r'^Bot(?!.*GPT)', case=False, na=False)]

        tot_gpt_winners += gpt_players["Winner"].sum()
        tot_bot_winners += bot_players["Winner"].sum()

    win_stats = {"GPT": (tot_gpt_winners/len(original_files)) * 100, "Bot": (tot_bot_winners/len(original_files)) * 100}
    return  pd.DataFrame(win_stats.items(), columns=['Player', 'Winner Percent'])


def summarize(path_to_save, file_list, original_files):
    with pd.ExcelWriter(os.path.join(path_to_save, "summarize.xlsx")) as writer:
        narrator_votes_averages = compute_combined_averages(file_list, 'Narrator Votes Stats', 
                                                            ['percent_voted_by_all', 'percent_voted_by_none', 'percent_voted_by_someone'])
        narrator_votes_averages.to_excel(writer, sheet_name='Narrator Votes Averages')

        votes_not_narrator_averages = compute_combined_averages(file_list, 'Votes When Not Narrator',
                                                                ['percent_voted_when_not_narrator'])
        votes_not_narrator_averages.to_excel(writer, sheet_name='Votes Not Narrator Averages')

        correct_votes_averages = compute_combined_averages(file_list, 'Correct Votes Stats',
                                                        ['percent_correct_votes_for_narrator'])
        correct_votes_averages.to_excel(writer, sheet_name='Correct Votes Averages')

        win_stats = compute_winners_stats(original_files)
        win_stats.to_excel(writer, sheet_name='Winners Statistics', index=False)

if __name__ == "__main__":

    args = argument_parsing()
    data_folder = args.data_folder

    for dir_path, _, filenames in os.walk(data_folder):
        analysis_files = []
        original_files = []
        for file_name in filenames:
            path_to_file = os.path.join(dir_path, file_name)
            path_to_save = os.path.join(dir_path, file_name[:-5] + "_analysis.xlsx")

            create_analysis(path_to_file, path_to_save)
            analysis_files.append(path_to_save)
            original_files.append(path_to_file)

        if len(analysis_files) != 0:
            summarize(dir_path, analysis_files, original_files)

        