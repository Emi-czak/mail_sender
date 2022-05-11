""" Database connectivity and mail handling """
from collections import namedtuple
from datetime import datetime, timedelta
from os import getenv
from string import Template
import sqlite3
from dotenv import load_dotenv
from dbcontext import DatabaseContext
from mailcontext import MailContext

Policy = namedtuple('Policy','firstname, surname, email, car_brand, \
            car_model, car_numbers, expirity_date')

def read_template(filename):
    """ Read message template from file

    Args:
        filename (str): path to txt file with message template

    Returns:
        string.Template: string with message template
    """
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def select_nearly_expire(database_connection, days_to_expire = 30):
    """Select policies with nearly expire date.

    Args:
        database_connection: connection to database
        days_to_expire (int): numbers of days to policy expiration

    Returns:
        list: list of policies with almost expire date
    """
    policy_list = []
    with DatabaseContext(database_connection) as database:
        database.cursor.execute("""SELECT
            customer_firstname,
            customer_surname,
            customer_mail,
            car_brand,
            car_model,
            car_number,
            expiry_date
        FROM policy 
        WHERE expiry_date <= ?""",(datetime.now()+timedelta(days=days_to_expire),))
        for firstname, surname, email, car_brand, car_model, car_numbers, expirity_date\
            in database.cursor.fetchall():
            policy_list.append(Policy(firstname, surname, email, car_brand,\
                car_model, car_numbers, expirity_date))
    return policy_list

if __name__ == '__main__':
    load_dotenv()
    ssl_enable = False
    smtp_server = getenv('SMTP_SERVER')
    port = getenv('PORT')
    msg_template = read_template('message_temp.txt')
    sender = 'worker_mail@company.xo'
    connection = sqlite3.connect('insurance.db')
    policies = select_nearly_expire(connection)
    mail_subject = 'Your policy is nearly expired.'
    with MailContext(smtp_server, port, ssl_enable) as connection:
        connection.connection.login(getenv('LOGIN'), getenv('PASSWORD'))
        for policy in policies:
            message = msg_template.substitute(
                customer = policy.firstname,
                vehicle = policy.car_brand,
                model = policy.car_model,
                car_numbers = policy.car_numbers,
                expirity_date = policy.expirity_date,
                worker_fn = getenv('FIRST_NAME'),
                worker_sn = getenv('LAST_NAME')
            )
            connection.sendmail(sender, policy.email, mail_subject, message)
            print(f'Sending email to: {policy.email}')
