from flask import render_template, request, Blueprint

page_base = Blueprint('page_base', __name__)

@page_base.route('/')
def index():
    return render_template('index.html')

@page_base.route('/about')
def about():
    return render_template('about.html')

@page_base.route('/search')
def search():
    return render_template('search.html')

@page_base.route('/thanks')
def thanks():
    return render_template('thanks.html')

@page_base.route('/sold')
def sold():
    locationId = request.args.get('locationId')
    return render_template('sold.html', locationId=locationId)
