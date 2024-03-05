import time
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, Configuration
import urllib3
from exchangelib.ewsdatetime import EWSDateTime
import argparse
from datetime import datetime
from exchangelib.errors import TransportError
import os

BaseProtocol.USERAGENT = "Auto-Reply/0.1.0"
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter  # 忽略TLS验证错误
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 禁用所有的InsecureRequestWarning警告


def Replace_str(str1):
    str_pattern = ['\\', '/', ':', '?', '*', '<', '>', '|', '"']
    res_str = str1
    for char in str_pattern:
        res_str = res_str.replace(char, '_')
    return res_str


def trans_time(time_string):
    time_str = EWSDateTime.from_string(time_string)
    return time_str


def Get_mails(account, sign_time, mail_user):
    for item in account.inbox.all().order_by('-datetime_received'):
        if item.datetime_received < sign_time:
            print(f"No more emails in {mail_user}'s inbox!")
            break
        else:
            email_name = item.subject
            os.makedirs(mail_user, exist_ok=True)
            saved_name = f'{mail_user}/{Replace_str(email_name)}.eml'
            if os.path.exists(saved_name) and item.size == os.path.getsize(saved_name):
                continue
            with open(saved_name, 'wb') as f:
                f.write(item.mime_content)
            print(f'{saved_name} has been saved')
    for item in account.sent.all().order_by('-datetime_received'):
        if item.datetime_received < sign_time:
            print(f"No more emails in {mail_user}'s sent_box!")
            break
        else:
            email_name = item.subject
            os.makedirs(mail_user, exist_ok=True)
            saved_name = f'{mail_user}/{Replace_str(email_name)}.eml'
            if os.path.exists(saved_name) and item.size == os.path.getsize(saved_name):
                continue
            with open(saved_name, 'wb') as f:
                f.write(item.mime_content)
            print(f'{saved_name} has been saved')


def Auth(server_name, mail_users, mail_pass, user, pass_hash, work_type, sign_time, user_sids):
    if not work_type:
        credentials = Credentials(username=user, password=pass_hash)
        config = Configuration(server=server_name, credentials=credentials)
        account = Account(primary_smtp_address=user, config=config, autodiscover=False, access_type=IMPERSONATION)
        for mail_user, user_sid in zip(mail_users, user_sids):
            account.identity.sid = user_sid
            Get_mails(account, sign_time, mail_user)
    else:
        for mail_user, password in zip(mail_users, mail_pass):
            credentials = Credentials(username=mail_user, password=password)
            config = Configuration(server=server_name, credentials=credentials)
            account = Account(primary_smtp_address=mail_user, config=config, autodiscover=False, access_type=DELEGATE)
            Get_mails(account, sign_time, mail_user)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--type',
                        help='''The manner of working.
                        0 -- An Impersonation user to get all emails.  
                        1 -- Provided the emails and the hashes(passwords) of users''', required=True, type=int)
    parser.add_argument('-s', '--server', help='The url(ip) of the exchange server')
    parser.add_argument('-u', '--username', help='The impersonation user that used to get emails')
    parser.add_argument('-p', '--password', help='The password(NTLM hash) of the impersonation user')
    parser.add_argument('-c', '--conf', help='The configuration that record the time of get emails')
    parser.add_argument('-pa', '--path', help='The path of the user_emails\' list', required=True)

    args = parser.parse_args()
    work_type = args.type
    username = args.username
    password = args.password
    server = args.server
    path = args.path
    conf = args.conf

    user_emails = []
    user_auth = []
    user_sid = []
    with open(path, 'r') as f:
        users_info = f.read().splitlines()
        for item in users_info:
            user_info = item.split(' ')
            user_emails.append(user_info[0])
            user_sid.append(user_info[2])
            if work_type:
                user_auth.append(user_info[1])

    with open(conf, 'r') as f:
        time_str = f.read()
    sign_time = trans_time(time_str)

    max_retries = 3
    time_delay = 5

    for attempt in range(max_retries):
        try:
            Auth(server, user_emails, user_auth, username, password, work_type, sign_time, user_sid)

            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
            with open(conf, 'w') as f:
                f.write(current_time)

            print('\nFinished!')
            break
        except TransportError:
            if attempt < max_retries - 1:
                print(f"连接超时，{time_delay}秒后尝试重连，这是第{attempt+1}/{max_retries}次尝试\n")
                time.sleep(time_delay)
            else:
                print("已经达到最大重试次数\n\n!!!----与服务器连接超时，请检查网络及目标服务器状态")
