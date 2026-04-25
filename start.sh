#!/bin/bash
cd /var/www/funca/tienda
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5001 app:app
