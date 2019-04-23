drop table if exists activity;
CREATE TABLE `activity`(
`serial` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`activity_code`  varchar(64) DEFAULT NULL COMMENT '活动代码',
`activity_title` varchar(64) DEFAULT NULL COMMENT '活动标题',
`activity_abstract` varchar(255) DEFAULT NULL COMMENT '活动摘要(富文本除图片)',
`activity_content` BLOB DEFAULT NULL COMMENT '活动内容(富文本)',
`activity_type` tinyint(1) DEFAULT NULL COMMENT '活动形式:1线上 2线下 3线上线下',
`has_lottery` tinyint(1) DEFAULT NULL COMMENT '是否有抽奖1是2否',
`lottery_type` tinyint(1) DEFAULT NULL COMMENT '抽奖形式1线下2线上3线上线下',
`activity_sort` tinyint(2) DEFAULT NULL COMMENT '活动内容分类:1成果推介活动2需求推介活动3 转化活动4 融资交流活动5供需交流活动6 项目合作活动7 服务推荐活动8专利申请培训活动9 对接会 10直播类 11其他',
`activity_site` varchar(64) DEFAULT NULL COMMENT '线上活动url(活动详情页面或直播类活动链接)',
`district_id` bigint(20) unsigned DEFAULT NULL COMMENT '活动地区(线下活动时必填)',
`address` varchar(255) DEFAULT NULL COMMENT  '活动详细地址(线下活动时必填)',
`online_time` datetime DEFAULT NULL  COMMENT '上线时间(到达上线时间前台显示)',
`down_time` datetime DEFAULT NULL COMMENT '下架时间(到达下线时间前台不再显示)',
`signup_start_time` datetime DEFAULT NULL comment '报名开始时间',
`signup_end_time` datetime DEFAULT NULL comment '报名截止时间',
`activity_start_time` datetime DEFAULT NULL comment '活动开始时间',
`activity_end_time` datetime DEFAULT NULL comment '活动结束时间',
`top` tinyint(1) DEFAULT NULL COMMENT '是否置顶。 1置顶2不置顶',
`top_time` datetime DEFAULT NULL COMMENT '置顶时间',
`summary_time` datetime DEFAULT NULL COMMENT '总结时间',
`max_people_number` int(11) DEFAULT NULL COMMENT '活动最大参与人数',
`signup_check` tinyint(1) DEFAULT NULL COMMENT '报名是否需要审核1是2否(默认2不需审核)',
`signup_people_number` int(11) DEFAULT NULL COMMENT '报名人数',
`activity_summary` BLOB DEFAULT NULL COMMENT '活动总结(富文本)',
`reach_intent` varchar(255) DEFAULT NULL COMMENT '活动达成意向',
`state` tinyint(1) DEFAULT NULL COMMENT '活动状态0伪删除1已创建2已上线3报名中4进行中5已结束',
`insert_time`	datetime DEFAULT NULL  comment '创建时间',
`creater` varchar(32)  DEFAULT NULL COMMENT '活动创建人(account_code)',
primary key(serial),
UNIQUE KEY `index_activity_code` (`activity_code`),
Key `index_activity_title` (`activity_title`),
Key `index_activity_type` (`activity_type`),
Key `index_activity_sort` (`activity_sort`),
Key `index_state` (`state`)
)ENGINE=INNODB DEFAULT CHARSET=utf8 COMMENT='活动信息表';

drop table if exists activity_signup;
create table activity_signup(
`serial`  int unsigned not null auto_increment, 
`signup_code` varchar(64) DEFAULT NULL comment '报名编号',
`activity_code` varchar(64) DEFAULT NULL comment '活动编号',
`signup_name` varchar(32) DEFAULT NULL comment '报名者姓名(必填)',
`signup_mobile` varchar(11) DEFAULT NULL comment '报名者手机(必填)',	
`verify_code` varchar(32) DEFAULT NULL comment '手机短信验证码(必填)',
`signup_email` varchar(64) DEFAULT NULL comment '电子邮箱（提示报名者关于活动的通知发到邮箱，务必保证邮箱能收到邮件）',
`company_info` varchar(255) DEFAULT NULL comment '单位信息',					
`concern_content` varchar(255) DEFAULT NULL comment '比较关注的内容（文字填写）',	
`change_num`  tinyint(1) DEFAULT NULL comment '信息修改次数，最多三次',  
`check_state` tinyint(1) DEFAULT NULL COMMENT '活动报名审核状态0伪删除1通过2不通过(默认不需审核通过)',
`check_time`	datetime DEFAULT NULL comment '审核时间',
`insert_time`	datetime DEFAULT NULL comment '创建时间',
primary key(serial),
UNIQUE KEY `index_signup_code` (`signup_code`),
UNIQUE KEY `index_code_mobile` (`activity_code`,`signup_mobile`),
KEY `index_activity_code` (`activity_code`),
KEY `index_signup_mobile` (`signup_mobile`)
) engine=innodb   default  character set utf8 comment '活动报名表';


drop table if exists activity_gift;
create table activity_gift(
`serial`  int unsigned not null auto_increment, 
`gift_code` varchar(64) DEFAULT NULL comment '礼品编号',
`activity_code` varchar(64) DEFAULT NULL comment '活动编号',
`gift_name` varchar(32) DEFAULT NULL comment '活动礼品名称',
`gift_abstract` varchar(255) DEFAULT NULL comment '活动礼品描述 ',
`state` tinyint(1) DEFAULT NULL  comment '活动礼品状态:0伪删除1正常2禁用',
`insert_time` datetime comment '创建时间',
`creater` VARCHAR(32)  DEFAULT NULL COMMENT '礼品创建人(account_code)',
primary key(serial),
UNIQUE KEY `index_gift_code` (`gift_code`)
) engine=innodb   default  character set utf8 comment '活动礼品表';


insert into function_info(`func_code`,`func_name`,`func_memo`,`func_url`,`item_type`,`pfunc_code`,`func_order`,`state`,`creater`,`insert_time`,`update_time`) 
values('w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz','活动管理','活动管理',null,1,null,0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('1CZ8YvtIxR3xBeziLwmTUYwp5UdoW9Hz','活动管理','活动管理','/activity/index/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('5bW84w8G8wb1Z8H7dupmooiOqXPUTxZm','活动报名管理','活动报名管理','/activity/signup/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('z4TEhrDPSXFaf6nMoXGFsNTrrbXGYhA2','活动礼品管理','活动礼品管理','/activity/gift/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('1Z8HFaf6nMoXGFsNTr6nMoXGaix02u3l','活动总结','活动总结','/activity/summary/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20')


insert into role_func_info(`role_code`,`func_code`,`state`,`creater`,`insert_time`,`update_time`)
values('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','1CZ8YvtIxR3xBeziLwmTUYwp5UdoW9Hz',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','5bW84w8G8wb1Z8H7dupmooiOqXPUTxZm',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','z4TEhrDPSXFaf6nMoXGFsNTrrbXGYhA2',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','1Z8HFaf6nMoXGFsNTr6nMoXGaix02u3l',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20')

insert into attachment_file_type(`tcode`,`tname`,`tmemo`) 
values('0120','activityCover','活动宣传图'),
      ('0121','activityEditor','活动富文本编辑器'),
      ('0122','activityAttachment','活动附件'),
      ('0123','activitySummary','活动总结附件')