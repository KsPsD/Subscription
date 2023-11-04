#!/bin/bash


# 데이터베이스 마이그레이션
python src/manage.py migrate

# Django 개발 서버 시작
python src/manage.py runserver 0.0.0.0:8000
