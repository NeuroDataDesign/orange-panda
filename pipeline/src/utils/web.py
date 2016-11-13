"""Contains basic signal processing utilities.

"""
import pickle
import pandas as pd
from utils.get_data import make_h5py_object
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import h5py
import plotly.plotly as py
import plotly.graph_objs as go
from utils import plots
import set_keys
import os, sys
import ast
import zipfile
from preprocessing.preprocessing_scripts import prep_data

RESULTS='app/static/results/'

def get_s3(req):
    f_name, extension = os.path.splitext(req['fpath'])
    local_path = 'files/' + req['name'] + extension
    if os.path.isfile(local_path):
        html = prep_data(local_path, req['token'])
        save_prep(html, req['name'])
        return 'ok!'
    conn = S3Connection(os.environ['AWS_ACCESS_KEY'],
            os.environ['AWS_SECRET_KEY'])
    bucket = conn.get_bucket(req['bucket'], validate=False)
    s3path = req['fpath']
    key = Key(bucket, s3path)
    f = file(local_path, 'wb')
    def callback(togo, total):
        print "Got {0: 10d} Bytes out of {1:10d} Bytes".format(togo, total)
        if togo == total:
            print "Done! The path of the " + req['name'] + \
            		" file was returned."
    key.get_file(f, cb = callback)
    f.close()
    prep_report = prep_data(local_path, req['token'])
    save_prep(prep_report, f_name)
    return 'ok !'

def make_meda_html(file_name):
    fn = 'files/' + file_name + '.pkl'
    # Load data from file path
    with open(fn, 'rb') as f:
    	df = pickle.load(f)
    return plots.full_report(df)

def save_analysis(html_report, patient):
    # Create folder for results if doesn't exist
    # Also set path variables to save data to later
    res_path = RESULTS + patient + '/'
    if not os.path.exists(res_path):
        os.makedirs(res_path)
    with open(res_path + "post_report.html", 'w') as f:
        f.write(html_report)
    ziph = zipfile.ZipFile(res_path + '../' + patient + '.zip',
                'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(res_path):
        for file in files:
            ziph.write(os.path.join(root, file))
    ziph.close()
    return 'ok!'

def save_prep(html_report, patient):
    title = '<title> PANDA Pre </title>'
    theme = '<link href="http://thomasf.github.io/solarized-css/solarized-dark.min.css" rel="stylesheet"></link>'
    script = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'
    html_report = '<head>' + title + script + theme + '</head>' + html_report
    res_path = RESULTS + patient + '/'
    if not os.path.exists(res_path):
        os.makedirs(res_path)
    with open(res_path + "prep_report.html", 'w') as f:
        f.write(html_report)
    return True

def _make_res(name):
    res = {
    'f_name': name,
            'prep_report': '/results/' + name + '/prep_report.html',
            'post_report': '/results/' + name + '/post_report.html',
            'zip': 'results/' + name + '.zip'
        }
    return res

def populate_table():
    for root, dirs, files in os.walk(RESULTS):
        return map(lambda x: _make_res(x), dirs)

