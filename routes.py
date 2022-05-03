from starlette.templating import Jinja2Templates
from models import Property

templates = Jinja2Templates(directory='templates')

async def homepage(request):
    try:
        filter = request.query_params['filter']

        if filter == 'under-100':
            data = request.state.db.listingsAndReviews.find({'$and':[{'cleaning_fee':{'$exists': True}},{'price': {'$lt': 100}}]}, limit=50)
        elif filter == 'highly-rated':
            data = request.state.db.listingsAndReviews.find({'$and':[{'cleaning_fee':{'$exists': True}},{'price': {'$lt': 100}},{'review_scores.review_scores_rating': {'$gt': 90}}]}, limit=50)
        elif filter == 'surprise':
            data = request.state.db.listingsAndReviews.find({'cleaning_fee':{'$exists': True},'amenities': {'$in': ["Pets allowed", "Patio or balcony", "Self check-in"]}}, limit=50)
    except KeyError:
        data = request.state.db.listingsAndReviews.find({'cleaning_fee':{'$exists': True}}, limit=50)

    response = []

    for doc in data:
        response.append(
            Property(
                doc['_id'],
                doc['name'], 
                doc['summary'], 
                doc['address']['street'], 
                str(doc['price']), 
                str(doc['cleaning_fee']),
                str(doc['accommodates']),
                doc['images']['picture_url'],
                doc['amenities']
            )
        )
    
    return templates.TemplateResponse('index.html', {'request': request, 'response': response})

async def listing(request):
    id = request.path_params['id']

    doc = request.state.db.listingsAndReviews.find_one({'_id': id})

    response = Property(
                doc['_id'],
                doc['name'], 
                doc['summary'], 
                doc['address']['street'], 
                str(doc['price']), 
                str(doc['cleaning_fee']),
                str(doc['accommodates']),
                doc['images']['picture_url'],
                doc['amenities']
            )

    return templates.TemplateResponse('listing.html', {'request': request, 'property': response})

async def confirmation(request):
    id = request.path_params['id']
    
    doc = request.state.db.bookings.insert_one({"property": id})

    name = request.state.db.listingsAndReviews.find_one({'_id': id})

    return templates.TemplateResponse('confirmation.html', {'request': request, 'confirmation': doc, 'name' : name['name']})

async def bookings(request):

    bookings = list(request.state.db.bookings.find())
    data = []
    for record in bookings:
        doc = request.state.db.listingsAndReviews.find_one({'_id': record['property']})
        data.append(doc['name'])

    return templates.TemplateResponse('bookings.html', {'request': request, 'bookings': data})