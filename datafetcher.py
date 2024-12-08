from apple_app_reviews_scraper import get_token, fetch_reviews
from app_store_scraper import AppStore
import requests
import time
from typing import List
import pandas as pd

###

# Consolidated Methods for fetching ids and reviews from the App Store

###


def get_reviews(app_name: str, num_reviews = 'all', country:str = 'us', as_df = False) -> List[str]:
    """
    Retrieve num_reviews number of reviews for a given app name

    Returns a json object of review and metadata.

    num_reviews can either be a number specifying number of reviews fetched or 'all' (default)

    as_df gives you the option to return reviews and metadata as a dataframe, otherwise this method will return reviews with metadata as json
    """

    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    ]

    app_id = AppStore(country=country, app_name=app_name).search_id()

    # Get initial token
    token = get_token(country, app_name, app_id, user_agents)
    
    # List to store reviews
    all_reviews = []
    
    # Initial offset
    offset = '1'
    
    # Flag to track if we should continue fetching
    continue_fetching = True
    
    while continue_fetching:
        try:
            # Fetch a batch of reviews
            reviews, new_offset, status_code = fetch_reviews(
                country, app_name, app_id, user_agents, token, offset
            )


            if num_reviews == 'all':
                all_reviews.extend(reviews)
                # Update offset or stop if no more reviews
                if new_offset is None or len(reviews) == 0:
                    continue_fetching = False
                    break
            else:
                num_reviews = int(num_reviews)
                if len(all_reviews) + len(reviews) <= num_reviews:
                    # Add reviews to the collection
                    all_reviews.extend(reviews)
                else:
                    num_reviews_left = num_reviews - len(all_reviews)
                    if len(reviews) < num_reviews_left:
                        # if there are no more reviews to fill up requested number of reviews just add the most reviews
                        all_reviews.extend(reviews)
                    else:
                        all_reviews.extend(reviews[:num_reviews_left-1])
                    continue_fetching = False
                    break
            
            # Update offset for next iteration
            offset = new_offset
            
            # Optional: print progress
            print(f"Total reviews collected: {len(all_reviews)}")
            
            # Optional: Add a delay to be nice to the API
            time.sleep(1)
        
        except Exception as e:
            print(f"Error occurred: {e}")
            # Optional: break or continue based on error
            break
    
    if as_df:
        reviews_df = pd.json_normalize(all_reviews)
        reviews_df['app_name'] = app_name
        renamed_reviews_df = reviews_df.rename(columns=lambda x: x.replace("attributes.", "") if x.startswith("attributes.") else x)
        return renamed_reviews_df

    return all_reviews