# based on https://github.com/catalyst-cloud/catalystcloud-price-comparison/blob/master/cloud_price_comparison.ipynb

import tika
tika.initVM()
from tika import parser

import re
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import requests
import json
import re
from bs4 import BeautifulSoup

def create_dir_if_not_exists(rel_dir_path):
    if not os.path.exists(rel_dir_path):
        os.makedirs(rel_dir_path)
        
create_dir_if_not_exists('dataset')
create_dir_if_not_exists('predicted-dataset')

usd_to_eur_exchange_rate_url = 'https://free.currencyconverterapi.com/api/v6/convert?q=USD_EUR&compact=ultra&apiKey=e9928ac3dd8a2341a6a4'

usd_to_eur_exchange_rate_json = requests.get(usd_to_eur_exchange_rate_url).json()
usd_to_eur_exchange_rate = float(usd_to_eur_exchange_rate_json['USD_EUR'])

# Betacloud

betacloud_url = 'https://pricing.betacloud.io/'
betacloud_data_location = 'dataset/betacloud_price_data.csv'
betacloud_gst_exclusive = True

betacloud_price_page_html = requests.get(betacloud_url).text
betacloud_price_page = BeautifulSoup(betacloud_price_page_html, 'html.parser')

betacloud_price_table = betacloud_price_page.find('table').tbody
betacloud_price_rows = betacloud_price_table.find_all('tr')

betacloud_prices_list = []

for row in betacloud_price_rows:
    betacloud_price_cells = list(row.stripped_strings)

    betacloud_prices_list.append({
        'Name': betacloud_price_cells[0],
        'vCPU': float(betacloud_price_cells[1]),
        'RAM, GB': float(betacloud_price_cells[2]),
        'Price per hour, EUR': float(betacloud_price_cells[4].strip('$')),
#        'SSD storage, GB': float(betacloud_price_cells[3]),
        'SSD storage, GB': .0,
        'HDD storage, GB': .0
    })

# Convert to csv
betacloud_dataframe = pd.DataFrame(betacloud_prices_list)
betacloud_dataframe.to_csv(betacloud_data_location)

print('Downloaded Betacloud prices, with {} items.'.format(betacloud_dataframe.shape[0]))

# Netways

netways_url = 'https://nws.netways.de/products/openstack'
netways_data_location = 'dataset/netways_price_data.csv'
netways_gst_exclusive = True

netways_price_page_html = requests.get(netways_url).text
netways_price_page = BeautifulSoup(netways_price_page_html, 'html.parser')

netways_price_div = netways_price_page.find(id='preconf1')
netways_price_table = netways_price_div.find('table').tbody
netways_price_rows = netways_price_table.find_all('tr')

netways_prices_list = []

for row in netways_price_rows:
    netways_price_cells = list(row.stripped_strings)

    if netways_price_cells[0].startswith('s2'):
        netways_prices_list.append({
            'Name': netways_price_cells[0],
            'vCPU': float(netways_price_cells[1]),
            'RAM, GB': float(netways_price_cells[2].strip('GB')),
            'Price per hour, EUR': float(netways_price_cells[8].strip('€')) / 30 / 24,
#            'SSD storage, GB': float(netways_price_cells[3].strip('GB')),
            'SSD storage, GB': .0,
            'HDD storage, GB': .0
        })

# Convert to csv
netways_dataframe = pd.DataFrame(netways_prices_list)
netways_dataframe.to_csv(netways_data_location)

print('Downloaded Netways prices, with {} items.'.format(netways_dataframe.shape[0]))

# Teutostack

teutostack_url = "https://teutostack.de/wp-content/uploads/2019/01/out_teutostack_teutostack-leistungsverzeichnis-2019-01-28.pdf"
teutostack_data_location = 'dataset/teutostack_price_data.csv'
teutostack_gst_exclusive = True

teutostack_prices_list = []

parsed = parser.from_file('/tmp/out_teutostack_teutostack-leistungsverzeichnis-2019-01-28.pdf')
content = parsed["content"]
result = re.findall("^(standard.*) (.*) Core.*, (.*) GiB RAM, (.*) GiB local Disc (.*)€ €.*$", content, re.MULTILINE)

for entry in result:
    name, vcpus, ram, storage, price = entry

    teutostack_prices_list.append({
        'Name': name,
        'vCPU': float(vcpus),
        'RAM, GB': float(ram),
        'Price per hour, EUR': float(price.replace(",", ".")),
#        'SSD storage, GB': float(storage),
        'SSD storage, GB': 0,
        'HDD storage, GB': .0
    })

# Convert to csv
teutostack_dataframe = pd.DataFrame(teutostack_prices_list)
teutostack_dataframe.to_csv(teutostack_data_location)

print('Downloaded Teutostack prices, with {} items.'.format(teutostack_dataframe.shape[0]))

# OVH

ovh_url = 'https://www.ovh.com/world/public-cloud/instances/prices/'
ovh_data_location = 'dataset/ovh_price_data.csv'
ovh_gst_exclusive = True

ovh_price_page_html = requests.get(ovh_url).text
ovh_price_page = BeautifulSoup(ovh_price_page_html, 'html.parser')

ovh_price_table = ovh_price_page.find_all('table')[1].tbody
ovh_price_rows = ovh_price_table.find_all('tr')

ovh_prices_list = []

for row in ovh_price_rows:
    namecol = row.find("td", {"class": "NAME"})
    ramcol = row.find("td", {"class": "RAM"})
    vcpuscol = row.find("td", {"class": "VCORE"})
    storagecol = row.find("td", {"class": "STOCKAGE"})
    pricecol = row.find("td", {"class": "PRICE"})

    name = list(namecol.stripped_strings)[0]
    ram = float(list(ramcol.stripped_strings)[0].split(" ")[0])
    vcpus = float(list(vcpuscol.stripped_strings)[0].split(" ")[0])
    storage = float(list(storagecol.stripped_strings)[0].split(" ")[0])
    price = float((pricecol.find(id="DE").get("data-price-hourly"))) * usd_to_eur_exchange_rate

    ovh_prices_list.append({
        'Name': name,
        'vCPU': vcpus,
        'RAM, GB': ram,
        'Price per hour, EUR': price,
#        'SSD storage, GB': storage,
        'SSD storage, GB': .0,
        'HDD storage, GB': .0
    })

# Convert to csv
ovh_dataframe = pd.DataFrame(ovh_prices_list)
ovh_dataframe.to_csv(ovh_data_location)

print('Downloaded OVH prices, with {} items.'.format(ovh_dataframe.shape[0]))

# Citycloud

citycloud_url = 'https://www.citycloud.com/pricing/'
citycloud_data_location = 'dataset/citycloud_price_data.csv'
citycloud_gst_exclusive = True

citycloud_price_page_html = requests.get(citycloud_url).text
citycloud_price_page = BeautifulSoup(citycloud_price_page_html, 'html.parser')

citycloud_price_table = citycloud_price_page.find('table').tbody
citycloud_price_rows = citycloud_price_table.find_all('tr')

citycloud_prices_list = []

for row in citycloud_price_rows:
    citycloud_price_cells = list(row.stripped_strings)
    eur_price = float(citycloud_price_cells[3].strip('$')) * usd_to_eur_exchange_rate

    citycloud_prices_list.append({
        'Name': citycloud_price_cells[0],
        'vCPU': float(citycloud_price_cells[1]),
        'RAM, GB': float(citycloud_price_cells[2]),
        'Price per hour, EUR': eur_price,
        'SSD storage, GB': .0,
        'HDD storage, GB': .0
    })

# Convert to csv
citycloud_dataframe = pd.DataFrame(citycloud_prices_list)
citycloud_dataframe.to_csv(citycloud_data_location)

print('Downloaded Citycloud prices, with {} items.'.format(citycloud_dataframe.shape[0]))

# Azure

azure_url = 'https://azureprice.net/?currency=EUR&region=westeurope'
azure_data_location = 'dataset/azure_price_data.csv'
azure_gst_exclusive = True

azure_price_page_html = requests.get(azure_url).text
azure_price_page = BeautifulSoup(azure_price_page_html, 'html.parser')

azure_price_script = azure_price_page.find('body').script.getText().strip()[7:][:-1]
azure_price_json = json.loads(azure_price_script)

azure_prices_list = []

for flavor in azure_price_json:
    if flavor['name'].startswith('Standard_B'):
        azure_prices_list.append({
            'Name': flavor['name'],
            'vCPU': float(flavor['numberOfCores']),
            'RAM, GB': float(flavor['memoryInMB'] / 1024),
            'Price per hour, EUR': float(flavor['linuxPrice']),
            'SSD storage, GB': .0,
#            'HDD storage, GB': float(flavor['osDiskSizeInMB']),
            'HDD storage, GB': .0
    })

# Convert to csv
azure_dataframe = pd.DataFrame(azure_prices_list)
azure_dataframe.to_csv(azure_data_location)

print('Downloaded Azure prices, with {} items.'.format(azure_dataframe.shape[0]))

# OTC

otc_url = "https://open-telekom-cloud.com/resource/blob/data/160462/0662e233681ca01247fef6a386c62d81/open-telekom-cloud-leistungsbeschreibung.pdf"
otc_data_location = 'dataset/otc_price_data.csv'
otc_gst_exclusive = True

otc_prices_list = []

parsed = parser.from_file('/tmp/open-telekom-cloud-leistungsbeschreibung.pdf')
content = parsed["content"]
regex = r"(s2\..*)\n\n(\d+)\s(\d+)\sOpen\sLinux\s(\d+,\d+)\s"
matches = re.finditer(regex, content, re.MULTILINE)

for match in matches:
    name, vcpus, ram, price = match.groups()
    otc_prices_list.append({
        'Name': name,
        'vCPU': float(vcpus),
        'RAM, GB': float(ram),
        'Price per hour, EUR': float(price.replace(",", ".")),
        'SSD storage, GB': float(storage),
        'SSD storage, GB': 0,
        'HDD storage, GB': .0
    })

# Convert to csv
otc_dataframe = pd.DataFrame(otc_prices_list)
otc_dataframe.to_csv(otc_data_location)

print('Downloaded OTC prices, with {} items.'.format(otc_dataframe.shape[0]))

# AWS

aws_url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/eu-central-1/index.json'
aws_raw_location = 'dataset/raw_aws_bulk.json'
aws_acceptable_instance_families = [
    'General purpose',
    'Micro instances'
]
aws_data_location = 'dataset/aws_price_data.csv'
aws_gst_exclusive = True

aws_bulk_json_request = requests.get(aws_url)
aws_bulk_json = aws_bulk_json_request.json()
with open(aws_raw_location, 'w') as aws_raw_file:
    json.dump(aws_bulk_json, aws_raw_file)

# Getting the instance products

with open(aws_raw_location, 'r') as aws_raw_file:
    aws_raw_json = json.load(aws_raw_file)
        
    aws_instances_list = []
            
    for product in aws_raw_json['products']:
        
        productFamily = aws_raw_json['products'][product]['productFamily']
        
        # Check product is compute instance
        if productFamily == 'Compute Instance':
                        
            # Check if instance is appropriate
            instanceFamily = aws_raw_json['products'][product]['attributes']['instanceFamily']
            is_current_gen = aws_raw_json['products'][product]['attributes']['currentGeneration'] == 'Yes'
            is_linux = aws_raw_json['products'][product]['attributes']['operatingSystem'] == 'Linux'
            no_preInstalledSw = aws_raw_json['products'][product]['attributes']['preInstalledSw'] == 'NA'
            is_shared_instance = aws_raw_json['products'][product]['attributes']['tenancy'] == 'Shared'

            if instanceFamily in aws_acceptable_instance_families and is_current_gen \
                and is_linux and no_preInstalledSw and is_shared_instance:
                
                # Append if appropriate
                aws_instances_list.append(product)

with open(aws_raw_location, 'r') as aws_raw_file:
    
    aws_prices_list = []
    
    for instance_key in aws_instances_list:

        attributes = aws_raw_json['products'][instance_key]['attributes']
                    
        # Get vCPU and RAM
        vCPU = float(attributes['vcpu'].replace(',',''))
        RAM = float(attributes['memory'].split(' ')[0].replace(',',''))

        # Break storage spec into array
        storage_strings = attributes['storage'].split(' ')

        # Find where the numbers end (200 x 1), and the description of the storage type (SSD) starts.
        final_num_index = None
        for word in storage_strings[::-1]:
            try:
                float(word.replace(',', ''))
                final_num_index = storage_strings.index(word)
                break
            except:
                foo = None

        # If there are no numbers in the storage spec, there is no storage included
        if final_num_index == None:

            total_ssd = .0
            total_hdd = .0

        # Else...
        else:

            # Perform the math to figure out how many GB of storage is included
            storage_calcs = storage_strings[0:final_num_index+1]
            storage_volume = eval(' '.join(['*' if x=='x' else x.replace(',', '') for x in storage_calcs]))

            # discern the type of storage
            if 'HDD' in storage_strings:                        
                total_ssd = .0
                total_hdd = float(storage_volume)

            elif 'SSD' in storage_strings:                        
                total_ssd = float(storage_volume)
                total_hdd = .0
            else: 
                total_ssd = float(storage_volume)
                total_hdd = .0


        # Get the price per USD
        terms = aws_raw_json['terms']['OnDemand'][instance_key]
        usd_price = None
        for specific_term in terms:
            for dimension_key in terms[specific_term]['priceDimensions']:
                dimension = terms[specific_term]['priceDimensions'][dimension_key]
                if dimension['unit'] != 'Hrs': raise ValueError("This price isn't in hours")
                usd_price = float(dimension['pricePerUnit']['USD'])

        # Convert to EUR
        eur_price = usd_price * usd_to_eur_exchange_rate
                
        # Append to list of prices
        aws_prices_list.append({
            'Name': attributes['instanceType'],
            'vCPU': vCPU,
            'RAM, GB': RAM,
            'Price per hour, EUR': eur_price,
#            'SSD storage, GB': total_ssd,
#            'HDD storage, GB': total_hdd
            'SSD storage, GB': .0,
            'HDD storage, GB': .0
        })

# Convert to CSV
aws_dataframe = pd.DataFrame(aws_prices_list)
aws_dataframe.to_csv(aws_data_location)

print('Downloaded AWS prices, with {} items.'.format(aws_dataframe.shape[0]))

# GCE

google_url = 'https://cloud.google.com/compute/pricing'
google_price_type = 'ffurt-hourly'
google_acceptable_instance_families = [
    'standard_machine_types'
]
google_data_location = 'dataset/google_price_data.csv'
google_gst_exclusive = True

google_price_page_html = requests.get(google_url).text
google_price_page = BeautifulSoup(google_price_page_html, 'html.parser')

# Extract the USD price per vCPU and per GB RAM
google_custom_compute_price_table = google_price_page.find(id='custommachinetypepricing').find_next('table')
google_custom_compute_rows = google_custom_compute_price_table.find_all('tr')[1:]

google_per_vcpu_usd = float(google_custom_compute_rows[0].find_all('td')[1][google_price_type].split()[0].strip('$'))
google_per_ram_usd = float(google_custom_compute_rows[1].find_all('td')[1][google_price_type].split()[0].strip('$'))

def most_freq_num(text):
    number_list = re.findall('\d*\.?\d+', text)
    most_frequent_num = max(set(number_list), key=number_list.count)
    return float(most_frequent_num)

google_prices_list = []

for instance_type in google_acceptable_instance_families:
    
    google_price_table = google_price_page.find(id=instance_type).find_next('table')
    google_rows = google_price_table.find_all('tr')[1:-1]
        
    for row in google_rows:
        
        # Extract number of vCPUs and GB of RAM
        try:
            cells = row.find_all('td')
            name = cells[0].get_text().strip()
            # Ignore if has lake in name (to remove skylake instances)
            if 'lake' in name:
                continue
            cpu_val = most_freq_num(str(cells[1]))
            ram_val = most_freq_num(str(cells[2]))
        except:
            foo='bar'
                        
        # Calcluate EUR price
        usd_price = (google_per_ram_usd * ram_val) + (google_per_vcpu_usd * cpu_val)
        eur_price = usd_price * usd_to_eur_exchange_rate
        
        try:
            google_prices_list.append({
                'Name': name,
                'vCPU': cpu_val,
                'RAM, GB': ram_val,
                'Price per hour, EUR': usd_price,
                'SSD storage, GB': .0,
                'HDD storage, GB': .0
            })
        except:
            continue

google_dataframe = pd.DataFrame(google_prices_list)
google_dataframe.to_csv(google_data_location)

print('Downloaded Google prices, with {} items.'.format(google_dataframe.shape[0]))

betacloud_dataset = pd.read_csv(betacloud_data_location, index_col=0)
netways_dataset = pd.read_csv(netways_data_location, index_col=0)
teutostack_dataset = pd.read_csv(teutostack_data_location, index_col=0)
ovh_dataset = pd.read_csv(ovh_data_location, index_col=0)
citycloud_dataset = pd.read_csv(citycloud_data_location, index_col=0)
google_dataset = pd.read_csv(google_data_location, index_col=0)
otc_dataset = pd.read_csv(otc_data_location, index_col=0)
aws_dataset = pd.read_csv(aws_data_location, index_col=0)
azure_dataset = pd.read_csv(azure_data_location, index_col=0)

def filter_dataset (dataset):
    without_high_ram = dataset[(dataset['RAM, GB'] <= 360) & (dataset['vCPU'] <= 64)]
    
    return without_high_ram

betacloud_dataset = filter_dataset(betacloud_dataset)
netways_dataset = filter_dataset(netways_dataset)
teutostack_dataset = filter_dataset(teutostack_dataset)
ovh_dataset = filter_dataset(ovh_dataset)
citycloud_dataset = filter_dataset(citycloud_dataset)
google_dataset = filter_dataset(google_dataset)
otc_dataset = filter_dataset(otc_dataset)
aws_dataset = filter_dataset(aws_dataset)
azure_dataset = filter_dataset(azure_dataset)

def split_dataset (dataset):
    x = dataset[["vCPU", "RAM, GB", "HDD storage, GB", "SSD storage, GB"]].values
    y = dataset["Price per hour, EUR"].values
    
    return (x, y)

betacloud_x, betacloud_y = split_dataset(betacloud_dataset)
netways_x, netways_y = split_dataset(netways_dataset)
teutostack_x, teutostack_y = split_dataset(teutostack_dataset)
ovh_x, ovh_y = split_dataset(ovh_dataset)
citycloud_x, citycloud_y = split_dataset(citycloud_dataset)
google_x, google_y = split_dataset(google_dataset)
otc_x, otc_y = split_dataset(otc_dataset)
aws_x, aws_y = split_dataset(aws_dataset)
azure_x, azure_y = split_dataset(azure_dataset)

# Initialise regressors
betacloud_linear = LinearRegression()
netways_linear = LinearRegression()
teutostack_linear = LinearRegression()
ovh_linear = LinearRegression()
citycloud_linear = LinearRegression()
google_linear = LinearRegression()
otc_linear = LinearRegression()
aws_linear = LinearRegression()
azure_linear = LinearRegression()

# Train regressors
betacloud_linear.fit(betacloud_x, betacloud_y)
netways_linear.fit(netways_x, netways_y)
teutostack_linear.fit(teutostack_x, teutostack_y)
ovh_linear.fit(ovh_x, ovh_y)
citycloud_linear.fit(citycloud_x, citycloud_y)
google_linear.fit(google_x, google_y)
otc_linear.fit(otc_x, otc_y)
aws_linear.fit(aws_x, aws_y)
azure_linear.fit(azure_x, azure_y)

# Predict Betacloud X
netways_betacloud_price = netways_linear.predict(betacloud_x)
teutostack_betacloud_price = teutostack_linear.predict(betacloud_x)
ovh_betacloud_price = ovh_linear.predict(betacloud_x)
citycloud_betacloud_price = citycloud_linear.predict(betacloud_x)
google_betacloud_price = google_linear.predict(betacloud_x)
otc_betacloud_price = otc_linear.predict(betacloud_x)
aws_betacloud_price = aws_linear.predict(betacloud_x)
azure_betacloud_price = azure_linear.predict(betacloud_x)

def pred_save (origin_flavors, provider_names, predictions):
    
    flavor_data = origin_flavors[["Name", "vCPU", "RAM, GB", "HDD storage, GB", "SSD storage, GB"]]
    
    for index, provider in enumerate(predictions):
        unit_string = ' price per hour, EUR'
        company_name = provider_names[index]
        flavor_data[company_name + unit_string] = predictions[index]
    
    return flavor_data

final_betacloud_data = pred_save(
    betacloud_dataset,
    [
        "Betacloud", "Citycloud", "Google", "AWS", "OVH", "Teutostack", "Azure", "Netways", "OTC"
    ], [
        betacloud_y, citycloud_betacloud_price, google_betacloud_price, aws_betacloud_price, ovh_betacloud_price, teutostack_betacloud_price, azure_betacloud_price, netways_betacloud_price, otc_betacloud_price
    ])

print('Saving resulting datasets.')

final_betacloud_data.to_csv('predicted-dataset/predicted_betacloud_prices.csv')
