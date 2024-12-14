# App Store Recommendation Algorithm

Create a data visualization dashboard to capture emotion/sentiment of user reviews on a specified iOS or Android App.

## Getting Started

Clone this repository:

    git clone https://github.com/ryanjewik/MGSC_final.git

Make virtual environment:
    
    python3 -m venv env

Activate virtual environment:

    .\env\Scripts\activate

Or activating virtual enviroment for MacOS/Linux

    source ./env/bin/activate

Install dependencies:

    pip3 install -r requirements.txt

Run flask app:

    python3 -m flask run --port 8000

## Deployment

Check the official Flask Deployment Guide for ways to deploy this Flask Application

https://flask.palletsprojects.com/en/stable/deploying/

## Acknowledgments

Libraries used to scape App Store Reviews

- https://pypi.org/project/app-store-scraper/
- https://github.com/glennfang/apple-app-reviews-scraper



# App Store Recommendation Algorithm

## Acknowledgments

- https://pypi.org/project/app-store-scraper/
- https://github.com/glennfang/apple-app-reviews-scraper


make virtual environment:
    
    python3 -m venv env

    .\env\Scripts\activate

install dependencies:

    pip install -r requirements.txt

put this in your env/pyvenv.cfg

    FLASK_APP=app.py
    FLASK_ENV=development

run flask app:

    python -m flask run --port 8000

Operating the app:

     - the search bar is used to search the app you want to perform sentiment analysis on
     - toggle for "deep" analysis is for sentence-by-sentence NLP techniques, more advanced and smoother spider graphs but longer run time
     - additional toggle for Android and IOS, IOS can only grab 20 reviews at a time so it will take longer. Additionally IOS scraper can have issues if there are no reviews on the app store page.
