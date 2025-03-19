#!/bin/bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m gunicorn app:app