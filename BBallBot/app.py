import re   # for regular expression
import time # for sleeping the bot
import os   # for files
import praw # the api for interacting with reddit
import requests # required by praw
import pandas   # for dataframes
from tabulate import tabulate   # to convert the dataframe to mark_down
from nba_api.stats.endpoints import playerfantasyprofilebargraph    # get player stats
from nba_api.stats.static import players    # get player ids to pull stats


# Connect to Reddit
def authenticate():
    reddit = praw.Reddit('BBallBot', user_agent="NBA Stat Bot:v1.0 (by u/BBallBot)")
    return reddit


# convert the names of the players to player ids
def convert_names(player_list):
    # this is hold the id from converting the player names to use in the api call
    player_ids = []

    # convert player names to player ids
    for player in player_list:
        if players.find_players_by_full_name(player):
            p = players.find_players_by_full_name(player)
            player_ids.append(p[0]["id"])

    return player_ids


def create_dataframe(player_ids):
    # create the dataframe and initialize with the first player
    season_stats = playerfantasyprofilebargraph.PlayerFantasyProfileBarGraph(player_id=player_ids[0])
    stats = season_stats.get_data_frames()[0]
    df = pandas.DataFrame(stats)

    # add all additional players mentioned in reddit comment to he dataframe
    for player in player_ids[1:]:
        season_stats = playerfantasyprofilebargraph.PlayerFantasyProfileBarGraph(player_id=player)
        stats = season_stats.get_data_frames()[0]
        df = df.append(stats)

    # drop some unneeded columns for formatting
    df = df.drop(columns=["PLAYER_ID", "TEAM_ID", "TEAM_ABBREVIATION", "FAN_DUEL_PTS", "NBA_FANTASY_PTS"])

    # set the indices to start at 1
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1
    
    return df

## df.to_markdown can not be posted directly so the comment must be read in from a txt file
def reply_comment(df, comment):
    with open("Output.txt", "w") as text_file:
        print(df.to_markdown(), file=text_file)

    with open("Output.txt", "r") as text_file:
        comment.reply(text_file.read())

# df.to_markdown can not be posted directly so the comment must be read in from a txt file
def reply_submission(df, submission):
    with open("Output.txt", "w") as text_file:
        print(df.to_markdown(), file=text_file)

    with open("Output.txt", "r") as text_file:
        submission.reply(text_file.read())

# put the players specified in comment in player_list
# convert the player_list to player_ids
# post the table as a comment
def comment_players(reddit, already_done):
    
    for comment in reddit.subreddit('test').comments(limit=10):
        # if the comment has not already been responded to skip
        if comment.id not in already_done and re.findall("(?<=\[)([^]]+)(?=\])", comment.body) and comment.author != reddit.user.me():
            # regex to extract player names from comments and store in player_list
            player_list = re.findall("(?<=\[)([^]]+)(?=\])", comment.body)
            
            # strip the remaining characters from the player names
            for i in range(len(player_list)):
                player_list[i] = player_list[i].replace("\\", "")
                player_list[i] = player_list[i].replace("[", "")

            # convert the player names to ids
            player_ids = convert_names(player_list)

            if player_ids:
                df = create_dataframe(player_ids)
                reply_comment(df, comment)

            # append the comment id to already done
            already_done.append(comment.id)

            with open("already_done.txt", "a") as f:
                f.write(comment.id + "\n")


# put the players specified in submission in player_list
# convert the player_list to player_ids
# post the table as a comment
def submission_players(reddit, already_done):
    for submission in reddit.subreddit('test').new(limit=10):
        # if the comment has not already been responded to and the comment is not the bot itself
        if submission.id not in already_done and re.findall("(?<=\[)([^]]+)(?=\])", str(submission.selftext)):
            text = str(submission.selftext)
            player_list = re.findall("(?<=\[)([^]]+)(?=\])", text)

            # strip the remaining characters from the player names
            for i in range(len(player_list)):
                player_list[i] = player_list[i].replace("\\", "")
                player_list[i] = player_list[i].replace("[", "")

            player_ids = convert_names(player_list)
            
            # if there is an error in the [[player name]]
            # player_ids will be an empty list
            if player_ids:
                df = create_dataframe(player_ids)
                reply_submission(df, submission)

            # append the comment id to already done
            already_done.append(submission.id)

            with open("already_done.txt", "a") as f:
                f.write(submission.id + "\n")

# keep a running list of all comment/submmissions replied to to prevent multiple replies 
def get_replied_to():
    if not os.path.isfile("already_done.txt"):
        already_done = []
    else:
        with open("already_done.txt", "r") as f:
            already_done = f.read()
            already_done = already_done.split("\n")
            already_done = filter(None, already_done)
            already_done = list(already_done)

    return already_done

def main():
    reddit = authenticate()
    # This loads the already parsed comments from a backup text file
    already_done = get_replied_to()

    while True:
        submission_players(reddit, already_done)
        comment_players(reddit, already_done)
        time.sleep(10)

if __name__ == '__main__':
    main()