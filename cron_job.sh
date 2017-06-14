#!/bin/bash

# Django 1.11 compatible


find $(pwd) -iname \*.pyc -exec rm -rfv {} \; #to delete all .pyc files

DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR
source ../venv/bin/activate
#source ./bin/activate
python pi_server/scan_machines.py
#python offline_reconnect.py
python manage.py initialize_machines
python manage.py generate_checksum
touch index.wsgi
python manage.py log_generator

#python log_generator.py
date > date.txt
sleep 2

cp map_machine_ids.txt shared/
