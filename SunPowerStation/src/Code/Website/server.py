from flask import Flask
from routes.main import main_routes

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(main_routes)





# HERE U can connect the database
# here u can connect and evaluate threads
# here u can connect and evaluate mqtt-connections



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)

