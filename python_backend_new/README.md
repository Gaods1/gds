#更改字段设置的字段
## AccountInfo
### account_code 
修改默认值为32位uuid
### state
修改为默认值为1
### insert_time
增加 auto_now_add 为True （增加记录是自动添加程序内不可更改）
### update_time
增加 auto_now 为True（更改记录时自动更改时间，程序内不可更改）