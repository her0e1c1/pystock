import requests

URL = "https://www.quandl.com/api/v3/databases.json"
r1 = requests.get(URL)
for d in r1.json()['databases']:
    print(d['database_code'])

    # {'downloads': 516416, 'premium': False, 'datasets_count': 12, 'description': "The U.S. Treasury ensures the nation's financial security, manages the nation's debt, collects tax revenues, and issues currency, provides data on yield rates.", 'image': 'https://quandl-data-upload.s3.amazonaws.com/uploads/source/profile_image/70/thumb_imgres-1.jpg', 'id': 70, 'name': 'US Treasury', 'database_code': 'USTREASURY'}
