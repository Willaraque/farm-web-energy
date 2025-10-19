''' Modulos a Utilizar'''
# ===========================================
import os, sys, shutil, re, calendar, json
from os import remove, rmdir
from shutil import rmtree, move
from pandas import ExcelWriter
from ast import Continue, Return
from pymongo import MongoClient
from bson import ObjectId
from copy import deepcopy
import numpy as np
import pandas as pd
import zipfile, csv, time, shutil, glob, requests, selectors
from pyunpack import Archive #Extraer los .zip or .rar
from functools import wraps
import functools
from pytz import timezone
from datetime import date, datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.etree.ElementTree import tostring


'''Modulos para utilizar multiprocesos'''
import multiprocessing as mp 
from multiprocessing import Process, Pool, cpu_count 
import itertools
from itertools import combinations

"""Modulo para leer XML"""
#=======================================
import xml.etree.ElementTree as ET

''' Modulos para utilizar en las clases'''
# ===========================================
from dataclasses import dataclass, field
from pydantic import BaseModel
from typing import Optional, Any, Callable, Tuple, Union, List
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

'''Modulo de envios de correos'''
# ==============================================
import smtplib
from smtplib import SMTP
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

'''Modulo de Web-Scrapping'''
# ==============================================
from bs4 import BeautifulSoup as bs
import html5lib
import lxml
import random, time, urllib
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc


'Establece el idioma a español, para las fechas'
# # ================================================
# import locale
# locale.setlocale(locale.LC_ALL, "es")

'''Quitar warning pandas'''
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter(action='ignore', category=FutureWarning)



''' Modulos para las Clases'''
# ===========================================
from fastapi import FastAPI, Form
from typing import Annotated, Any, Callable, Optional, List, Union
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, GetJsonSchemaHandler, PydanticUserError
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
import logging

'''Modulos para encriptar contraseñas'''
import bcrypt
from copy import deepcopy
from passlib.context import CryptContext

from BaseDatos.clases import CreateUser, UpdateUser, Task, UpdateTask, User, UserInDB, Token, RefreshToken, TokenData, RefreshTokenData, IdMongo, MarketData, MarketDataResponse
from BaseDatos.productos import (get_all_tasks, 
                                create_one_task,
                                get_one_task,
                                get_one_task_id,
                                update_task,
                                delete_one_task,
                                )   

from BaseDatos.usuarios import (create_one_user, 
                                get_one_user,
                                get_all_users, 
                                get_one_user_id,
                                update_user,
                                delete_user) 

from BaseDatos.token import (create_access_token,
                            create_refresh_token,
                            get_user, 
                            verify_password,
                            authenticate_user,
                            save_token,
                            update_token,
                            get_token,
                            verify_token,
                            verify_refresh_token,
                            drop_tokenBD, 
                            get_user_current,
                            get_user_active_current)

from Utilities.db_connection import *
from Utilities.Comprobaciones_horarias import *
from Utilities.Data_Utils import *
from OMIE.OMIE import *
from OMIE.PreciosOMIE import *
from REE.Liquidacion import *
from REE.WebScrapping import *
   
from BaseDatos.TablaPrecios import Admin, get_all_prices  

