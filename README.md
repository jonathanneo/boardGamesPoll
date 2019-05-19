# boardGamesPoll README  
## Purpose  
The purpose of this web application is to provide a board games ranking website for board games players around the world. We saw the lack of polling websites for board games and decided to create a more modern and functional web application for this purpose. The social choice mechanism we used is the first-past-the-post voting, enabling users to create polls where they can then add options which other users (only logged in users) can vote for which option suits the poll best.  

## Architecture  
The architectural pattern that we are using is the Model View Controller, where the we have three separate aspects: the model, controller, and the view. The model is where data storage and database related actions take place, demonstrated in "models.py". The controller is the link that is responsible to build from the database, prepares the view and updates the models back to the database, which takes place ini "routes.py" as well as "forms.py". The view is what the user sees, which is included in the .html files. 

## Local Launch
go to the project directory and type the following commands in your CLI:  
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

## Deployment on Heroku
We have deployed the application on Heroku servers into two seperate environments:
* Staging: https://board-games-poll.herokuapp.com
* Production: https://boardgamespoll.herokuapp.com

Staging will be used for testing purposes before promoting to production. We have also enabled automated deployment such that every new git commit to the repository will result in a re-deployment of the application to reflect the latest commit.   

## Pipelines on Heroku
We have created automated CI pipelines on Heroku. When a pull request is created, an app will automatically be created to allow developers to view and test the app. 
After testing is performed on the new app and pushed to Staging, the staging-app can be pushed into production using the Heroku GUI by: 
1. Promote to production 
2. Promote
3. App is now in production and the staging branch merged into master branch
    
![ImageOfHeroku](https://github.com/jonathanneo/images/blob/master/heroku_1_annotated.png?raw=true) 
![ImageOfHeroku](https://github.com/jonathanneo/images/blob/master/heroku_2_annotated.png?raw=true)


## Product Tracking Board
Our team uses a Trello Board to manage cards (tasks) with checklists (sub-tasks) to allow us to work more effectively. To gain access to the Trello board, please contact @jonathanneo. 

![ImageOfTrelloBoard](https://github.com/jonathanneo/images/blob/master/Trello_img.PNG?raw=true) 
