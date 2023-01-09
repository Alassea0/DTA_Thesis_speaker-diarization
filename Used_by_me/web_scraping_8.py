from requests import get
from bs4 import BeautifulSoup
import pandas as pd 


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
                 # Compiling the episode info
                 episode_data = [season, episode_number, title, rating, total_votes]

                 # Append the episode info to the complete dataset
                 series_episodes.append(episode_data)
                 
    series_episodes_df = pd.DataFrame(series_episodes, columns = ['season', 'episode_number', 'title', 'rating', 'total_votes'])
    return series_episodes_df

# Men
spartacus_id = "tt1442449"
narcos_id = "tt2707408"
thewire_id = "tt0306414"
punisher_id = "tt5675620"

# Women
bridgerton_id = "tt8740790"
jane_id = "tt3566726"
gossip_id = "tt0397442"
pretty_id = "tt1578873"

all_ids = [spartacus_id, narcos_id, thewire_id, punisher_id, bridgerton_id, jane_id, gossip_id, pretty_id]

def make_url(id):
    result = "https://www.imdb.com/title/" + id + "/episodes?season="
    return result

urls = []
for id in all_ids:
    url = make_url(id)
    urls.append(url)

seasons = [3, 3, 3, 2, 2, 2, 2, 2]
df_list = []
for url, season in zip(urls, seasons):
    df = get_ratings(url, season)
    df_list.append(df)

titles = ["spartacus_ratings", "narcos_ratings", "thewire_ratings", "thepunisher_ratings", "bridgerton_ratings", "jane_the_virgin_ratings", "gossip_girl_ratings", "pretty_little_liars_ratings"]

def remove_str(votes):
    for r in ((',',''), ('(',''),(')','')):
        votes = votes.replace(*r)
    return votes

for df, title in zip(df_list, titles):
    df['total_votes'] = df['total_votes'].apply(remove_str).astype(int)
    df['rating'] = df['rating'].astype(float)
    df.to_csv("./Data/" + title + ".csv", index=False) 



