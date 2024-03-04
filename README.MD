```sh
python Exchange_Get.py -t 0 -s test.com -u administrator@test.com -p 84830468d80ef86dee1c4597ff70419c:84830468d80ef86dee1c4597ff70419c -c 1.ini -pa mailbox.txt # 用hash收取邮件

python Exchange_Get.py -t 0 -s test.com -u administrator@test.com -p 1qaz2wsx!@# -c 1.ini -pa mailbox.txt # 用密码收取邮件

python Exchange_Get.py -t 1 -s test.com -u administrator@test.com -p 84830468d80ef86dee1c4597ff70419c:84830468d80ef86dee1c4597ff70419c -c 1.ini -pa mailbox.txt # 当使用1模式时，-u和-p两个选项失效。程序将会从mailbox中获取凭证收取邮件
```
mailbox格式如下
```text
邮箱名 口令 用户sid
```
sid号可通过以下命令获取
```sh
wmic useraccount where name='username' get sid
```

1.ini格式如下，标志着所收取邮件的接收时间，每次收取邮件后会自动更新
```text
2024-03-04 23:21
```
如果使用0模式收邮件，需要将一个用户添加到Exchange server的 IMPERSONATION角色

```sh
python Exchange_Get.py -h
usage: Exchange_Get.py [-h] -t TYPE [-s SERVER] [-u USERNAME] [-p PASSWORD] [-c CONF] -pa PATH

options:
  -h, --help            show this help message and exit
  -t TYPE, --type TYPE  The manner of working. 0 -- An Impersonation user to get all emails. 1 -- Provided the emails
                        and the hashes(passwords) of users
  -s SERVER, --server SERVER
                        The url(ip) of the exchange server
  -u USERNAME, --username USERNAME
                        The impersonation user that used to get emails
  -p PASSWORD, --password PASSWORD
                        The password(NTLM hash) of the impersonation user
  -c CONF, --conf CONF  The configuration that record the time of get emails
  -pa PATH, --path PATH
                        The path of the user_emails' list
```
