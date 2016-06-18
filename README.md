# plantalytics-backend
[![Coverage Status](https://coveralls.io/repos/github/Plantalytics/plantalytics-backend/badge.svg?branch=master)](https://coveralls.io/github/Plantalytics/plantalytics-backend?branch=master)
[![Build Status](https://travis-ci.org/Plantalytics/plantalytics-backend.svg?branch=master)](https://travis-ci.org/Plantalytics/plantalytics-backend)

## License

Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing, Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley.

This project is licensed under the MIT License. Please see the file LICENSE in this distribution for license terms.

## How to Run Locally

So you'd like to give this project a spin? You're in luck, follow these
instructions for success! To start, you'll need to obtain the following:

* **Python** (version 3 or greater)
  * https://www.python.org/downloads/
* **Django** (version 1.9 or greater)
  * See below for installation.
* **Text Editor** (or **IDE**, *PyCharm* is worth a try ;) )
  * https://www.jetbrains.com/pycharm/download/#section=windows

After successfully installing Python and/or your Text Editor/IDE, it's recommended you set up a virtual environment.

To enable a virtual environment using python 3, first install virtualenv with the following command:
```
    pip install virtualenv
```
Then from inside your project directory use the following command:
```
    virtualenv -p python3 venv
```
Next activate the virtual environment, to ensure you have a clean environment for development.
```
    source venv/bin/activate
```
To turn the virtual environment off, simply type `deactivate`
Once the environment is on, install the required dependencies:
(Patience please, this may take a few minutes..._literally_)
```
    pip install -r requirements.txt
```

Next, run the following command:

```
    python src/manage.py runserver
```

To run tests locally use the following:
```
    python src/manage.py test dummy
```
where 'dummy' is the suits associated with the 'dummy' application page.

Once the development server is up and running, launch a web browser
and go to the following URL:

* http://localhost:8000/dummy/

If successful, you should see the following message:

* *Hello , Plantalytics World!! Welcome to the backend, where things ain't pretty, but they get stuff DONE!*

**Did you see it? Congrats!! You're a *backend dev* now!**

<img src="http://cdn-assets.insomniac.com/images/news/GIF%20Dance%20Party.gif">
