# Appointment Scheduler App

This application manages doctor's appointments

## Setup

Before you can run or deploy the sample, you will need to do the following:

Install dependencies, preferably with a virtualenv:

    $ py -m venv venv
    $ venv\Scripts\activate
    $ pip install -r requirements.txt

## Running locally

When running locally

    $ flask --app app run

If it happened that you accidentally deleted the instance\server.db file. Here are the steps to create new instance

    $  flask --app app init-db

This will recreate instance\server.db file and will create the following data:

Tables: `user_level`, `user`, `appointments`

User Level: `admin`, `scheduler`, `doctor`

User: `username: admin`, `password: admin`, `user_level_id: 3`, `email: arbenjohnavillanosa@gmail.com`

Scheduler: `username: scheduler1`, `password: scheduler1`, `user_level_id: 1`, `email: scheduler1@gmail.com`

Doctor: `username: doctor1`, `password: doctor1`, `user_level_id: 2`, `email: doctor1@gmail.com`

