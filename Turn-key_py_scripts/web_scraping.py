from requests import get
from bs4 import BeautifulSoup
import pandas as pd 
import argparse
import os


# Based on: https://isabella-b.com/blog/scraping-episode-imdb-ratings-tutorial/


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=dir_path, help="pass directory")
parser.add_argument("-id", "--show_identity", type=str, required=True, help="IMDb Identity number for show") # This can be found on IMDb, in the url for the show. It's usually (always?) "tt + number"
parser.add_argument("-s", "--season", type=int, default=1, help="Amount of seasons to scrape")
parser.add_argument("-t", "--title", type=str, required=True, help="TV show title")

args = parser.parse_args() 


def get_ratings(url, season:int):
    series_episodes = []

    # For every season in the series-- range depends on the show
    for sn in range(1,season+1):
           # Request from the server the content of the web page by using get(), and store the server’s response in the variable response
           response = get((url) + str(sn))

           # Parse the content of the request with BeautifulSoup
           page_html = BeautifulSoup(response.text, 'html.parser')

           # Select all the episode containers from the season's page
           episode_containers = page_html.find_all('div', class_ = 'info')

           # For each episode in each season
           for episodes in episode_containers:
                # Get the info of each episode on the page
                 season = sn
                 episode_number = episodes.meta['content']
                 title = episodes.a['title']
                 rating = episodes.find('span', class_='ipl-rating-star__rating').text
                 total_votes = episodes.find('span', class_='ipl-rating-star__total-votes').text
                 desc = episodes.find('div', class_='item_description').text.strip()
                 airdate = episodes.find('div', class_='airdate').text.strip()
                 # Compiling the episode info
                 episode_data = [season, episode_number, title, airdate, rating, total_votes, desc]

                 # Append the episode info to the complete dataset
                 series_episodes.append(episode_data)
                 
    series_episodes_df = pd.DataFrame(series_episodes, columns = ['season', 'episode_number', 'title', 'airdate', 'rating', 'total_votes', "description"])
    return series_episodes_df


url = "https://www.imdb.com/title/" + args.show_identity + "/episodes?season="


df = get_ratings(url, args.season)

def remove_str(votes):
    for r in ((',',''), ('(',''),(')','')):
        votes = votes.replace(*r)
    return votes


df['total_votes'] = df['total_votes'].apply(remove_str).astype(int)
df['rating'] = df['rating'].astype(float)
df.to_csv(args.path + args.title + "_ratings.csv", index=False) 







