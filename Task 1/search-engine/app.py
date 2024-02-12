# Importing Modules
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request
from crawler import crawl, search

# Flask App Instance
app = Flask(__name__)
app.add_url_rule('/photos/<path:filename>', endpoint='photos', view_func=app.send_static_file)

# Setting Scheduler to run weekly
weekly_scheduler = BackgroundScheduler()
weekly_scheduler.add_job(crawl, 'interval', weeks=1)
weekly_scheduler.start()

# Define Homepage route
@app.route('/', methods=['GET'])
def home():
    # Render search.html template
    return render_template('search.html')

# Define Search route
@app.route('/search', methods=['GET'])
def search_result():
    # Get query parameter input by user
    query = request.args.get('query')
    # Get the data from search function from crawler.py
    search_results = search(query)
    # Render result.html by sending search_result and query
    return render_template('result.html', search_results=search_results, query=query)

if __name__ == '__main__':
    app.run(debug=True)