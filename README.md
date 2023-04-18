# How to run

The app is located in the App folder.
The server script is located in the Server folder.

## Dependencies:

* Install the following packages using command prompt:
    pip install "kivy[full]" kivy_garden
    pip install kivymd
    pip install kivy_garden
    pip install requests
    pip install matplotlib
    garden install matplotlib
    pip install sqlalchemy
    pip install fastapi
    pip install "uvicorn[standard]"
    pip install pydantic 

## To set up the server:

    Note: I have changed the database connection to use sqlite which reduces setup time
    - Change directory to /Server
    - Run the command below:
        uvicorn main:app --reload
    - This will start the server. Leave this cmd window open. Use this to see requests and sql executed.
    
## To run the app:

    - Run the main.py file.
    
## There are no accounts preloaded so to create an account:

    - Create an account in the app.
    - When asked for verification code, look at command prompt window for server. 
    - The email address entered should be diaplyed along side a 6 digit code.
    - Enter this code into the app.
    - The same process should be followed when using 'forgot password'.
    
## Using the app:

    - To select muscles when creating a workout plan, press and hold on the button. This is buggy because of kivy.
    - To delete workout plans/workouts/exercises: 
        - Click and hold the image/icon first.
        - Then move cursor to right.
        - This should reveal a red delete button.
        - Press this button.
    - Use the refresh button in the top right to see changes after editing.
        
