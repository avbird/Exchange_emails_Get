from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, Configuration, FileAttachment
import urllib3
from exchangelib.ewsdatetime import EWSDateTime
import argparse
from datetime import datetime

BaseProtocol.USERAGENT = "Auto-Reply/0.1.0"
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter  # 忽略TLS验证错误
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 禁用所有的InsecureRequestWarning警告


def trans_time(time_string):
    time_str = EWSDateTime.from_string(time_string)
    return time_str


def Get_mails(account, sign_time):
    for item in account.inbox.all().order_by('-datetime_received'):
        if item.datetime_received < sign_time:
            print("No more emails in this user's mailbox!")
            break
        else:
            for attachment in item.attachments:
                if isinstance(attachment, FileAttachment):
                    name = f'{item.subject}-{attachment.name}'
                    with open(name, 'wb') as f, attachment.fp as fp:
                        buffer = fp.read(1024)
                        while buffer:
                            f.write(buffer)
                            buffer = fp.read(1024)
            with open(f'{item.subject}.eml', 'wb') as f:
                f.write(item.mime_content)


def Auth(server_name, mail_users, mail_pass, user, pass_hash, work_type, sign_time, user_sids):
    if not work_type:
        credentials = Credentials(username=user, password=pass_hash)
        config = Configuration(server=server_name, credentials=credentials)
        account = Account(primary_smtp_address=user, config=config, autodiscover=False, access_type=IMPERSONATION)
        for user_sid in user_sids:
            account.identity.sid = user_sid
            Get_mails(account, sign_time)
    else:
        for mail_user, password in zip(mail_users, mail_pass):
            print(mail_user, password)
            credentials = Credentials(username=mail_user, password=password)
            config = Configuration(server=server_name, credentials=credentials)
            account = Account(primary_smtp_address=mail_user, config=config, autodiscover=False, access_type=DELEGATE)
            Get_mails(account, sign_time)


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

    Auth(server, user_emails, user_auth, username, password, work_type, sign_time, user_sid)

    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    with open(conf, 'w') as f:
        f.write(current_time)

    print('Finished!')