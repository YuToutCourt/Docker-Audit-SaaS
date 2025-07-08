#!/bin/bash

source /opt/Docker-Audit-SaaS/venv/bin/activate

cd /opt/Docker-Audit-SaaS

screen -dmS api python3 app.py

