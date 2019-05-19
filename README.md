# boardGamesPoll README  
## Purpose  
The purpose of this web application is to provide a board games ranking website for board games players around the world. We saw the lack of polling websites for board games and decided to create a more modern and functional web application for this purpose. The social choice mechanism we used is the first-past-the-post voting, enabling users to create polls where they can then add options which other users (only logged in users) can vote for which option suits the poll best.  

## Architecture  
The architectural pattern that we are using is the Model View Controller, where the we have three separate aspects: the model, controller, and the view. The model is where data storage and database related actions take place, demonstrated in "models.py". The controller is the link that is responsible to build from the database, prepares the view and updates the models back to the database, which takes place ini "routes.py" as well as "forms.py". The view is what the user sees, which is included in the .html files. 

## Launch Tutorial  
go to the project directory and launch the following:  
```
virtualenv venv
source venv/bin/activate OR venv\Scripts\activate (Windows)
python ./setup.py
flask db init
flask db migrate
flask db upgrade
flask run
```
The web application should be hosted at http://localhost:5000.  

## Tests  
We have included a python and a Selenium test script for our web application. To run the Selenium test, simply go to the Selenium IDE in the browser and open the 'test.side' file. To run the python app, NEED TO BE COMPLETED, ADD JSFIDDLE TOO


