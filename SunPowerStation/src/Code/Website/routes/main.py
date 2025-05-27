from flask import Flask, render_template, request, Blueprint, jsonify
import json
import sqlite3
import os
from datetime import datetime


main_routes = Blueprint('main_routes', __name__, url_prefix='/')


@main_routes.route('/')
def index():
    return render_template('index.html', title = 'Home')

@main_routes.route('/test')
def test():
    return render_template('test.html')

@main_routes.route('/temperatur')
def temperatur():
    return render_template('temperatur.html', title = 'Temperatur')

@main_routes.route('/steuerung')
def steuerung():
    return render_template('steuerung.html', title = 'Steuerung')
