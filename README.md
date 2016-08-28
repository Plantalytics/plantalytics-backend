# Plantaltyics Back End
[![Coverage Status](https://coveralls.io/repos/github/Plantalytics/plantalytics-backend/badge.svg?branch=develop)](https://coveralls.io/github/Plantalytics/plantalytics-backend?branch=develop)
[![Build Status](https://travis-ci.org/Plantalytics/plantalytics-backend.svg?branch=develop)](https://travis-ci.org/Plantalytics/plantalytics-backend)

Plantalytics is an IoT web app intended to help vintners monitor conditions of 
their vineyards. The back end receives data from the hubs, provides support to 
the front end with a robust API, and integrates with an 
[Apache Cassandra cluster](http://cassandra.apache.org/).

This system was developed for 
[Plantalytics: Precision Agriculture](http://plantaltyics.us) as part 
of Portland State University's Computer Science Senior Capstone program.

## How to Run Locally

So you'd like to give this project a spin? You're in luck, follow these
instructions for success! To start, you'll need to obtain the following:

* **Python** (version 3 or greater)
  * https://www.python.org
* **Django** (version 1.9 or greater)
  * See below for installation.
* **Text Editor** (**Atom** is great! Or an **IDE**, *PyCharm* is worth a try! ;) )
  * https://atom.io
  * https://www.jetbrains.com/pycharm/

After successfully installing Python and/or your Text Editor/IDE, it's 
recommended you set up a virtual environment.

To enable a virtual environment using python 3, first install virtualenv with 
the following command:
```
    pip install virtualenv
```
Then from inside your project directory use the following command:
```
    virtualenv -p python3 venv
```
Next activate the virtual environment, to ensure you have a clean environment 
for development.
```
    source venv/bin/activate
```
To turn the virtual environment off, simply type `deactivate`
Once the environment is on, install the required dependencies:
(Patience please, this may take a few minutes..._literally_)
```
    pip install -r requirements.txt
```

To run tests locally use the following:
```
    cd src
    python manage.py test
```

Next, run the following command:
```
    python manage.py runserver
```
Once the development server is up and running, launch a web browser
and go to the following URL:

* http://localhost:8000/health_check

If successful, you should see the following response:

```
    {
          'isAlive': true,
    }
```

**Did you see it? Congrats!! You're *awesome* now! Let's dance.**

<img src="http://cdn-assets.insomniac.com/images/news/GIF%20Dance%20Party.gif">

For more information, including API details, please see the 
[documentation repository](https://github.com/Plantalytics/documentation).

## License

Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing, Matt Fraser, 
Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley.

This project is licensed under the MIT License. Please see the file LICENSE 
in this distribution for license terms.
