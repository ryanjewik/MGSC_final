from flask import Flask, render_template, request, jsonify
from transformers import pipeline
from flask import Flask
import pandas as pd
import matplotlib.pyplot as plt
from google_play_scraper import Sort, reviews_all, reviews, search
from app_store_scraper import AppStore
import numpy as np
import base64
from io import BytesIO


app = Flask(__name__)
# Initialize classifier
classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)
retrieval_limit = 400



@app.route("/")
def home():
    return render_template('index.html')



@app.route('/search', methods=['POST'])
def search_apps():
    app_search = request.form.get('app_search')
    is_ios = request.form.get('ios') == 'true'
    
    try:
        if is_ios:
            return jsonify({'error': 'iOS not implemented yet'})
        else:
            # Search for apps
            appIds, appNames = get_android_apps(app_search)
            # Process each app and generate graphs
            graphs = []
            for i in range(0, len(appIds)):
                # Get reviews
                df = get_android_reviews(appIds[i], appNames[i])
                # Analyze emotions
                emotion_df = analyze_app_emotions(df['review'], df['name'].iloc[0])
                
                # Generate graph
                img = create_emotion_spider(emotion_df, df['name'].iloc[0], 
                                        'blue' if i == 0 else 'green' if i == 1 else 'red',
                                        (10,10) if i == 0 else (6,6))
                
                graphs.append({
                    'name': df['name'].iloc[0],
                    'image': img,
                    'is_primary': i == 0
                })
                
            return render_template('results.html', graphs=graphs)
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
    
    
    
    
    
#functions
def create_emotion_spider(emotions_df, title_suffix, color, figsize):
    # Create buffer to store image
    from io import BytesIO
    import base64
    
    # Create figure and plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Calculate means and get top 6
    emotion_means = emotions_df.drop(['review', 'app_name'], axis=1).mean()
    top_emotions = dict(sorted(emotion_means.items(), key=lambda x: x[1], reverse=True)[:6])
    
    # Prepare data
    emotions = [emotion.capitalize() for emotion in top_emotions.keys()]
    values = list(top_emotions.values())
    
    # Setup angles
    num_vars = len(emotions)
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]
    values += values[:1]
    
    # Plot data
    ax.plot(angles, values, 'o-', linewidth=2, color=color, label='Top 6 Emotions')
    ax.fill(angles, values, alpha=0.25, color=color)
    
    # Customize chart
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(emotions, size=10)
    ax.set_rgrids([0.1, 0.2, 0.3, 0.4, 0.5])
    
    plt.title(f"Emotional Analysis: {title_suffix}", size=15, y=1.05)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.tight_layout()
    
    # Save plot to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode('utf-8')
    buffer.close()
    
    # Clear the current figure
    plt.close()
    
    # Encode
    
    
    return graph



def analyze_app_emotions(reviews, app_name):
    emotions_df = pd.DataFrame()
    skipped_count = 0
    
    for review in reviews:
        try:
            # Get emotions for current review
            emotions = classifier(review)
            
            # Create dictionary mapping labels to scores
            row_data = {'review': review, 'app_name': app_name}
            for emotion in emotions[0]:
                row_data[emotion['label']] = emotion['score']
                
            # Convert to DataFrame row and concatenate
            review_df = pd.DataFrame([row_data])
            emotions_df = pd.concat([emotions_df, review_df], ignore_index=True)
            
        except RuntimeError as e:
            skipped_count += 1
            continue
    
    return emotions_df

def get_android_apps(app_name):
    appIds = []
    appNames = []
    appsearch = app_name

    #app search
    result = search(
        appsearch,
        lang="en",  # defaults to 'en'
        country="us",  # defaults to 'us'
        n_hits=3  # defaults to 30 (= Google's maximum) we can adjust to how many other recommendations we might want
    )
    appIds.append(result[0]['appId'])
    appIds.append(result[1]['appId'])
    appIds.append(result[2]['appId'])
    appNames.append(result[0]['title'])
    appNames.append(result[1]['title'])
    appNames.append(result[2]['title'])
    
    return appIds, appNames


def get_android_reviews(app_id, appName):
    #adds all the reviews to a dataframe
    app_df = pd.DataFrame()
    result, _ = reviews(
        app_id,
        #sleep_milliseconds=0, # defaults to 0
        lang='en', # defaults to 'en'
        country='us', # defaults to 'us'
        sort=Sort.NEWEST, # defaults to Sort.MOST_RELEVANT
        count = retrieval_limit,
        #continuation_token=continuation_token
    )
    for review in result:
        developerResponse = review
        date = review['at']
        userName = review['userName']
        reviewText = review['content']
        score = review['score']
        #can't get title
        #can't get isEdited
        review_df = pd.DataFrame({'developerResponse': [developerResponse],  'date': [date], 'review': [reviewText], 
                                    'score': [score], 'userName': [userName],'name': [appName]})
        app_df = pd.concat([app_df, review_df], ignore_index = True)
    return app_df