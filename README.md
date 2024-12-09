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


