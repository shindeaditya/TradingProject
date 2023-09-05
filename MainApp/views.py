import csv
import pandas as pd
import json
import asyncio
from django.shortcuts import render, HttpResponse
from .forms import UploadCSVForm
from .models import Candle

async def process_csv(file_path, timeframe):
	df = pd.read_csv(file_path)
	data=[]

	max_high=0
	min_low=0
	volume=0
	temp_data=[]
	for ind in df.index:
	    volume=volume+df['VOLUME'][ind]
	    if(ind%timeframe==0):
	        max_high=df['HIGH'][ind]
	        min_low=df['LOW'][ind]
	        temp_data.append(df['BANKNIFTY'][ind])
	        temp_data.append(df['DATE'][ind])
	        temp_data.append(df['TIME'][ind])
	        temp_data.append(df['OPEN'][ind])


	    if(ind%timeframe==(timeframe-1)):
	        temp_data.append(max_high)
	        temp_data.append(min_low)
	        temp_data.append(df['CLOSE'][ind])
	        temp_data.append(volume)
	        data.append(temp_data)
	        temp_data=[]
	        volume=0

	    if(df['HIGH'][ind]>max_high):
	        max_high=df['HIGH'][ind]

	    if(df['LOW'][ind]<min_low):
	        min_low=df['LOW'][ind]

	candles = pd.DataFrame(data,columns=['BankNifty','Date','Time','Open','High','Low','Close','Volume'])
	return candles



def upload_csv_view(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            timeframe = form.cleaned_data['timeframe']
            file_path = 'path_to_store_uploaded_csv.csv'
            with open(file_path, 'wb') as destination:
                for chunk in csv_file.chunks():
                    destination.write(chunk)
            # Use asyncio to process the CSV file in the background
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            candles = loop.run_until_complete(process_csv(file_path, timeframe))
            # Store the converted data as a JSON file
            json_data = candles.to_json(orient ='records')
            json_file_path = 'path_to_store_json_output.json'
            with open(json_file_path, 'w') as json_file:
                json.dump(json_data, json_file, default=str)
            response = HttpResponse(json.dumps(json_data), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="output.json"'
            return response
    else:
        form = UploadCSVForm()
    return render(request, 'upload_csv.html', {'form': form})
