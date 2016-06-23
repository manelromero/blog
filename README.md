#Blog project
This is a fully functional blog application example for my [Udacity](http://www.udacity.com) Full Stack Web Developer Nanodegree. This application is made using **Python** and [Google App Engine](https://cloud.google.com/appengine/).

A working demo is available [here](http://skilful-album-134323.appspot.com/).

###Clone the application
* Clone this repository opening your terminal, going to the folder where you want to install it and typing

    ``` terminal
    git clone https://github.com/manelromero/blog.git
    ```

###Download the application
* Click [here](https://github.com/manelromero/blog/archive/master.zip) to download the application.
* Copy the downloaded `.zip` file to the folder where you want the application and uncompress it.

###Run the application
* To run this application, you need to have installed the **Google App Engine SDK**. Files needed and detailed instructions can be found [here](https://cloud.google.com/appengine/downloads).
* Open the Google App Engine SDK and create a new application introducing the folder where you installed the blog as _Application Directory_.
* Press `Run` and remember the _Port_ number.
* Open your browser and type `localhost:[Port]` in the address bar changing `[Port]` with your application _Port_ number

###Application
* This application is made to manage the classical blog page where users can sign up.
* An unregistered user will be able only to read the posts. 
* Any registered user, once logged in, can _create_ a post, _edit_ or _delete_ their own posts and _like_ or _dislike_ other user's posts.
* User must be also logged in to comment on posts.