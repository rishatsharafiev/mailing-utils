# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_PATH, '.env')
load_dotenv(DOTENV_PATH)

import logging
import pyodbc
import json
import requests
import math
from requests.auth import HTTPBasicAuth
from datetime import datetime

### logger
logger = logging.getLogger(__name__)
logger_handler = logging.FileHandler(os.path.join(BASE_PATH, '{}.log'.format(__file__)))
logger_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# logger.error('We have a problem')
# logger.info('While this is just chatty')

def main():

    ESPUTNIK_EMAIL = os.getenv('ESPUTNIK_EMAIL', '')
    ESPUTNIK_PASSWORD = os.getenv('ESPUTNIK_PASSWORD', '')
    ESPUTNIK_GROUP_CLIENT_INFO = os.getenv('ESPUTNIK_GROUP_CLIENT_INFO', '')
    ESPUTNIK_FIELD_PHONE=os.getenv('ESPUTNIK_FIELD_PHONE', '')
    ESPUTNIK_FIELD_CREATED_AT=os.getenv('ESPUTNIK_FIELD_CREATED_AT', '')
    ESPUTNIK_FIELD_BIRTH_DATE=os.getenv('ESPUTNIK_FIELD_BIRTH_DATE', '')
    ESPUTNIK_FIELD_SEX=os.getenv('ESPUTNIK_FIELD_SEX', '')
    ESPUTNIK_FIELD_FIRST_CALL=os.getenv('ESPUTNIK_FIELD_FIRST_CALL', '')
    ESPUTNIK_FIELD_LAST_CALL=os.getenv('ESPUTNIK_FIELD_LAST_CALL', '')


    MSSQL_DRIVER = os.getenv('MSSQL_DRIVER', '{FreeTDS}')
    MSSQL_TDS_VERSION = os.getenv('MSSQL_TDS_VERSION', 8.0)
    MSSQL_SERVER = os.getenv('MSSQL_SERVER')
    MSSQL_PORT = os.getenv('MSSQL_PORT', 1433)
    MSSQL_DATABASE = os.getenv('MSSQL_DATABASE')
    MSSQL_UID = os.getenv('MSSQL_UID')
    MSSQL_PWD = os.getenv('MSSQL_PWD')

    MSSQL_CONNECTION_STRING = 'DRIVER={DRIVER};' \
        'SERVER={SERVER};' \
        'PORT={PORT};' \
        'DATABASE={DATABASE};' \
        'UID={UID};' \
        'PWD={PWD};' \
        'TDS_Version={TDS_VERSION};'.format(
        DRIVER=MSSQL_DRIVER,
        TDS_VERSION=MSSQL_TDS_VERSION,
        SERVER=MSSQL_SERVER,
        PORT=MSSQL_PORT,
        DATABASE=MSSQL_DATABASE,
        UID=MSSQL_UID,
        PWD=MSSQL_PWD,
    )

    MSSQL_DATABASE_CONNECTION = pyodbc.connect(MSSQL_CONNECTION_STRING)

    MSSQL_DATABASE_CURSOR = MSSQL_DATABASE_CONNECTION.cursor()

    try:
        auth = HTTPBasicAuth(ESPUTNIK_EMAIL, ESPUTNIK_PASSWORD)
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        post_url = 'https://esputnik.com/api/v1/contacts'

        with MSSQL_DATABASE_CONNECTION:
            MSSQL_DATABASE_CURSOR.execute("\
                SELECT DISTINCT [Номер анкеты] AS form_id \
                    ,[Дата создания] AS created_at \
                    ,[Фамилия] AS surname \
                    ,[Имя] AS first_name \
                    ,[Отчество] AS second_name \
                    ,[Дата рождения] AS birth_date \
                    ,[Пол.Название] AS sex \
                    ,[Электронная почта] AS email \
                    ,[Основной телефон.Номер] AS phone \
                    ,[Первый звонок] AS first_call \
                    ,[Последний звонок] AS last_call \
                    ,[Первая встреча] AS first_meeting \
                    ,[Последняя встреча] AS last_meeting \
                    ,[TS] AS ts \
                FROM [a2profile_fh].[dbo].[tGetClientInfo] \
                WHERE [Электронная почта] IS NOT NULL AND [Электронная почта] != ''"
            )

            contacts_for_add = []

            for row in MSSQL_DATABASE_CURSOR.fetchall():
                form_id = row[0] or ''
                if row[1]:
                    created_at = row[1].strftime('%Y-%m-%d')
                else:
                    created_at = ''

                if row[2]:
                    surname = row[2].split('-')[0].capitalize() or ''
                else:
                    surname = ''

                if row[3]:
                    first_name = row[3].split('-')[0].capitalize() or ''
                else:
                    first_name = ''

                if row[4]:
                    second_name = row[4].split('-')[0].capitalize() or ''
                else:
                    second_name = ''

                if row[5]:
                    birth_date = row[5].strftime('%Y-%m-%d')
                else:
                    birth_date = ''

                sex = row[6] or ''
                email = row[7] or ''
                phone = row[8] or ''

                if row[9]:
                    first_call = row[9].strftime('%Y-%m-%d')
                else:
                    first_call = ''

                if row[10]:
                    last_call = row[10].strftime('%Y-%m-%d')
                else:
                    last_call = ''

                if row[11]:
                    first_meeting = row[11].strftime('%Y-%m-%d')
                else:
                    first_meeting = ''

                if row[12]:
                    last_meeting = row[12].strftime('%Y-%m-%d')
                else:
                    last_meeting = ''

                ts = row[13] or ''

                if email:
                    fields = []
                    if phone:
                        fields.append({
                            'id': ESPUTNIK_FIELD_PHONE,
                            'value': phone,
                        })
                    if created_at:
                        fields.append({
                            'id': ESPUTNIK_FIELD_CREATED_AT,
                            'value': created_at,
                        })
                    if birth_date:
                        fields.append({
                            'id': ESPUTNIK_FIELD_BIRTH_DATE,
                            'value': birth_date,
                        })
                    if sex:
                        fields.append({
                            'id': ESPUTNIK_FIELD_SEX,
                            'value': sex,
                        })
                    if first_call:
                        fields.append({
                            'id': ESPUTNIK_FIELD_FIRST_CALL,
                            'value': first_call,
                        })
                    if last_call:
                        fields.append({
                            'id': ESPUTNIK_FIELD_LAST_CALL,
                            'value': last_call,
                        })

                    contact = {
                        'firstName' : first_name,
                        'lastName' : surname,
                        'channels' : [
                            {
                                'type' : 'email',
                                'value' : email,
                            },
                        ],
                        'groups': [
                            {
                                'name': ESPUTNIK_GROUP_CLIENT_INFO,
                            }
                        ],
                        'fields': fields
                    }

                    contacts_for_add.append(contact)

            chunk_length = 3000 - 1
            steps = math.ceil(len(contacts_for_add) / chunk_length)
            body = {
                'contacts' : [],
                'dedupeOn' : 'email',
                # 'fieldId' : '',
                'contactFields' : [ 'firstName', 'lastName', ],
                'customFieldsIDs' : [
                    ESPUTNIK_FIELD_PHONE,
                    ESPUTNIK_FIELD_CREATED_AT,
                    ESPUTNIK_FIELD_BIRTH_DATE,
                    ESPUTNIK_FIELD_SEX,
                    ESPUTNIK_FIELD_FIRST_CALL,
                    ESPUTNIK_FIELD_LAST_CALL,
                ],
                'groupNames' : [ ESPUTNIK_GROUP_CLIENT_INFO, ],
                'groupNamesExclude' : [],
                'restoreDeleted' : True,
                'eventKeyForNewContacts' : '{group}_new_contact'.format(group=ESPUTNIK_GROUP_CLIENT_INFO)
            }

            for step in range(steps):
                chunk = contacts_for_add[step*chunk_length:chunk_length*(step + 1)]

                print(step*chunk_length, ' ', chunk_length*(step + 1), len(chunk))
                body['contacts'] = chunk

                response = requests.post(post_url, auth=auth , headers=headers, json=body)
                response_json = response.json()

                if response.status_code == 200:
                    failedContacts = response_json.get('failedContacts', '')
                    if isinstance(failedContacts, list):
                        print('failed: ', len(failedContacts))
                    else:
                        print('failed: ', failedContacts)
                else:
                    logger.exception(str(response_json))
                time.sleep(3)
    except Exception as e:
        logger.exception(str(e))

if __name__ == '__main__':
    main()
