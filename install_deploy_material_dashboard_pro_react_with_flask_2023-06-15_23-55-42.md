To install and deploy Material Dashboard Pro React with Flask, follow these steps:

1. Purchase and download the Material Dashboard Pro React from their official website (https://www.creative-tim.com/product/material-dashboard-pro-react).

2. Extract the downloaded zip file. You should see the React project folder.

3. Next, set up a new Flask project. To do this, create a new folder to store your Flask app and navigate to this folder in your terminal.

4. Install Flask and other necessary packages using pip:

```
pip install Flask Flask-Cors
```

5. Create a new Python file named `app.py` in the Flask project folder and add the following code:

```python
from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='react-app/build')
CORS(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(f"{app.static_folder}/{path}"):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

This code creates a minimal Flask app that serves the static files of the React app.

6. Configure your React app to use Flask's backend. Open the React project folder, then open the `package.json` file. Add the "proxy" key with the Flask app's URL:

```json
{
  ...
  "proxy": "http://localhost:8080",
  ...
}
```

7. Build your React app. Navigate to the React project folder in your terminal and run:

```
npm install
npm run build
```

This will create a `build` folder with the compiled React app.

8. Copy the `build` folder from your React app to the Flask app's folder. Inside your Flask project folder, you should have the following structure:

```
/your-flask-app-folder
    /react-app
        /build
    app.py
```

9. Run your Flask app using the terminal within the Flask project folder:

```
python app.py
```

10. Open your web browser and navigate to `http://127.0.0.1:8080`. You should see the Material Dashboard Pro React app.

That's it! You've successfully installed and deployed the Material Dashboard Pro React app with a Flask backend.