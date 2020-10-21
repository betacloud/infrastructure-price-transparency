# based on https://github.com/catalyst-cloud/catalystcloud-price-comparison/blob/master/deploy_graph.py

import datetime
import hashlib
import os
import shutil
import time

import jinja2
import pandas as pd

# Converts the csv at csv_path into an HTML graph
def csv_to_graph(csv_path):

    template_dir = 'templates'

    # Initalise jinga env and template
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir)
    )

    # Import cloud price data
    df = pd.read_csv(csv_path, index_col=0)

    # Sort by mean price across providers
    rows_to_get_mean = df[[
        'OVH price per hour, EUR',
        'Citycloud price per hour, EUR',
        'Google price per hour, EUR',
        'AWS price per hour, EUR',
        'Azure price per hour, EUR',
        'OTC price per hour, EUR',
    ]]

    df['Mean price per hour'] = rows_to_get_mean.mean(1)

    df = df.sort_values(by=['Mean price per hour'])

    # Generate hash of CSV used to generate graph.
    source_data_hash = hashlib.md5(open(csv_path,'rb').read()).hexdigest()
    source_data_hash = source_data_hash[:10]

    # Generate current date as string
    timestamp_string = time.strftime("%d/%m/%Y", time.localtime())

    # Define a function that removes empty decimal places from numbers ('16.0' to
    # '16') to shorten the labels on the graph without losing any detail.
    def shorten_num(float):
        if float.is_integer():
            return str(int(float))
        else:
            return str(float)

    # Extract labels from the csv, and format them as a string we can insert into
    # the template.
    names_list = []
    name_string = "{cpu} vCPUs, {ram} GB RAM"
    for index, row in df.iterrows():

        short_cpu = shorten_num(row['vCPU'])
        short_ram = shorten_num(row['RAM, GB'])

        formatted_name_string = name_string.format(cpu=short_cpu, ram=short_ram)

        names_list.append(formatted_name_string)
    names_list = ['"' + x + '"' for x in names_list]
    names_list = ', '.join(names_list)

    # Define fucntion that extracts prices from the csv and formats them as a string
    # we can insert into the template.
    def get_price_string(label):
        prices = list(df[label])
        prices = [format(x, '.3f') for x in prices]
        prices = ', '.join(prices)
        return prices

    # Extract price data.
    ovh_data = get_price_string('OVH price per hour, EUR')
    citycloud_data = get_price_string('Citycloud price per hour, EUR')
    google_data = get_price_string('Google price per hour, EUR')
    aws_data = get_price_string('AWS price per hour, EUR')
    otc_data = get_price_string('OTC price per hour, EUR')
    azure_data = get_price_string('Azure price per hour, EUR')

    # Create display directories if they don't already exist.
    if not os.path.exists('result'):
        os.makedirs('result')

    # Render the template with the labels and price data.
    graph_data_template = env.get_template('all.js')
    data_filled_js = graph_data_template.render(
        labels=names_list,
        today=datetime.datetime.now().strftime("%d.%m.%Y"),
        ovh_data=ovh_data,
        citycloud_data=citycloud_data,
        google_data=google_data,
        aws_data=aws_data,
        azure_data=azure_data,
        otc_data=otc_data
    )

    # Write the rendered template into a display file for use.
    with open('result/all.js', 'w') as graph_js:
        graph_js.write(data_filled_js)

    graph_data_template = env.get_template('small.js')
    data_filled_js = graph_data_template.render(
        labels='"1 vCPU, 1 GB RAM", "2 vCPUs, 2 GB RAM", "4 vCPUs, 4 GB RAM", "4 vCPUs, 8 GB RAM", "8 vCPUs, 16 GB RAM"',
        today=datetime.datetime.now().strftime("%d.%m.%Y"),
        ovh_data=str.join(", ", ovh_data.split(", ")[0:5]),
        citycloud_data=str.join(", ", citycloud_data.split(", ")[0:5]),
        google_data=str.join(", ", google_data.split(", ")[0:5]),
        aws_data=str.join(", ", aws_data.split(", ")[0:5]),
        azure_data=str.join(", ", azure_data.split(", ")[0:5]),
        otc_data=str.join(", ", otc_data.split(", ")[0:5])
    )

    # Write the rendered template into a display file for use.
    with open('result/small.js', 'w') as graph_js:
        graph_js.write(data_filled_js)

csv_path = 'predicted-dataset/predicted_citycloud_prices.csv'
csv_to_graph(csv_path)
