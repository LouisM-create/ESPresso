from flask import Flask, render_template, request, Blueprint, jsonify
import json

main_routes = Blueprint('main_routes', __name__, url_prefix='/')


@main_routes.route('/')
def index():
    return render_template('index.html', title = 'Home')

@main_routes.route('/test')
def test():
    return render_template('test.html')

@main_routes.route('/test2')
def test2():
    return render_template('index.html', title = 'not Home')

@main_routes.route('/temperatur')
def temperatur():
    return render_template('temperatur.html', title = 'Temperatur')

@main_routes.route('/heizung')
def heizung():
    return render_template('heizung.html', title = 'Heizung')