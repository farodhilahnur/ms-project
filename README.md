# projects

## Install Dependencies
```bash

# $ virtualenv venv
# $ . venv/bin/activate
$ pip install -r requirements.txt
```

## Model Migration
```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

## Run
```bash
$ python manage.py runserver
```


## 
REST-API berbasis Django yang menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) untuk mengelola project - campaign dan channel untuk manajemen data prospek. API ini dirancang untuk mencakup proses campaign dalam suatu project.
