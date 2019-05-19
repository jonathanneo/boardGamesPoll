# boardGamesPoll README  
## Purpose  
the purpose of the web application, explaining both the context and the social choice mechanism used.  
The purpose of this web application is to provide a board games ranking website for board games players around the world. We saw the lack of polling websites for board games and decided to create a more modern and functional web application for this purpose. The social choice mechanism we used is the first-past-the-post voting, enabling users to create polls where they can then add options which other users (only logged in users) can vote for which option suits the poll best.  

## Architecture  
the architecture of the web application  
The architectural pattern that we are using is the Model View Controller, where the we have three separate aspects: the model, controller, and the view. The model is where data storage and database related actions take place, demonstrated in "models.py". The controller is the link that is responsible to build from the database, prepares the view and updates the models back to the database, which takes place ini "routes.py" as well as "forms.py". The view is what the user sees, which is included in the .html files. 

## Launch Tutorial  
describe how to launch the web application.  

Include commit logs, showing contributions and review from both contributing students
Installation:  
virtualenv venv  
source venv/bin/activate (Linux)  
pip install flask  
pip install python-dotenv  
pip install flask-wtf  
pip install flask-sqlalchemy  
pip install flask-migrate  
pip install flask-login  
pip install flask-mail  
pip install pyjwt  
pip install flask-bootstrap  

Running the code:  
source venv/bin/activate  
python ./setup.py  

## Tests  
describe some unit tests for the web application, and how to run them.  


