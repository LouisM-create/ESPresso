from flask import Flask, render_template, request, Blueprint, jsonify
import json

main_routes = Blueprint('main_routes', __name__, url_prefix='/')


@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/test')
def test():
    return render_template('test.html')