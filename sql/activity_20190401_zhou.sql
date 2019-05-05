drop table if exists activity;
CREATE TABLE `activity`(
`serial` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`activity_code`  varchar(64) DEFAULT NULL COMMENT '活动代码',
`activity_title` varchar(64) DEFAULT NULL COMMENT '活动标题',
`activity_abstract` varchar(255) DEFAULT NULL COMMENT '活动摘要(富文本除图片)',
`activity_content` text DEFAULT NULL COMMENT '活动内容(富文本)',
`activity_type` tinyint(1) DEFAULT NULL COMMENT '活动形式:1线上 2线下 3线上线下',
`has_lottery` tinyint(1) DEFAULT NULL COMMENT '是否有抽奖1是2否',
`lottery_desc` text COMMENT '抽奖描述',
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
`activity_summary` text DEFAULT NULL COMMENT '活动总结(富文本)',
`contacter` varchar(32) default null comment '活动联系人',
`mobile` char(11) default  null comment '活动联系人手机号',
`reach_intent` varchar(255) DEFAULT NULL COMMENT '活动达成意向',
`state` tinyint(1) DEFAULT NULL COMMENT '活动状态0伪删除1已创建2已上线3报名中4待开始5进行中6已结束7已下架',
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
`account_code` varchar(32) DEFAULT NULL COMMENT '报名者账号',
`change_num`  tinyint(1) DEFAULT NULL comment '信息修改次数，最多三次',
`check_state` tinyint(1) DEFAULT NULL COMMENT '活动报名审核状态0伪删除1通过2不通过(默认不需审核通过)3待审核',
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

drop table if exists activity_comment;
create table activity_comment(
  `serial`  int unsigned not null auto_increment,
  `comment_code` varchar(64) not null default '' comment '评论编号',
  `activity_code` varchar(64) not null default '' comment '活动编号',
  `signup_code` varchar(64) not null default '' comment '报名编号',
  `comment` varchar(255) not null default '' comment '活动评论内容',
  `state` tinyint(1) unsigned not null default 2 comment '评论状态1提交等待审核2审核通过3审核未通过',
  `insert_time` datetime not null default '0000-00-00 00:00:00' comment '评论时间',
  primary key(serial),
  unique key `index_comment_code` (`comment_code`)
) engine=innodb   default  character set utf8 comment '活动评论表';

drop table if exists activity_lottery;
create table activity_lottery(
  `serial` int unsigned not null auto_increment,
  `lottery_code` varchar(64) not null default '' comment '抽奖编号',
  `activity_code` varchar(64) not null default '' comment '活动编号',
  `lottery_title` varchar(50) DEFAULT NULL COMMENT '抽奖标题',
  `type` tinyint(1) unsigned not null default 1 comment '抽奖形式1线上2线下',
  `start_time` datetime not null default '0000-00-00 00:00:00' comment '抽奖开始时间',
  `end_time` datetime not null default '0000-00-00 00:00:00' comment '抽奖结束时间',
  `state` tinyint(1) unsigned not null default 1 comment '抽奖状态1正常2禁用',
  `insert_time` datetime not null default '0000-00-00 00:00:00' comment '添加时间',
  primary key(serial),
  unique key `index_lottery_code` (`lottery_code`)
) engine=innodb default character set utf8 comment '活动抽奖表';

drop table if exists activity_prize;
create table activity_prize(
      `serial` int unsigned not null auto_increment,
      `prize_code` varchar(64) not null default '' comment '奖品编号',
      `lottery_code` varchar(64) not null default '' comment '抽奖编号',
      `prize_name` varchar(64) not null default '' comment '奖品名称',
      `prize_type` tinyint(1) unsigned not null default 0 comment '奖品类型0未中奖(谢谢参与)1一等奖2二等奖3三等奖4四等将',
      `probability` float(4,2) not null default 0.00 comment '概率',
      `prize_desc` varchar(255) not null default '' comment '奖品描述',
      `prize_num` int(10) unsigned not null default 1 comment '奖品数量',
      `remain_num` int(10) unsigned not null default 1 comment '剩余未抽中数量',
      `state` tinyint(1) unsigned not null default 1 comment '奖品状态1正常2禁用',
      `insert_time` datetime not null default '0000-00-00 00:00:00' comment '添加时间',
      primary key(serial),
      unique key `index_prize_code` (`prize_code`)
) engine=innodb default character set utf8 comment '抽奖奖品表';

drop table if exists activity_prize_winner;
create table activity_prize_winner(
      `serial` int unsigned not null auto_increment,
      `win_code` varchar(64) not null default '' comment '中奖记录编号',
      `activity_code` varchar(64) NOT NULL DEFAULT '' COMMENT '活动编号',
      `lottery_code` varchar(64) NOT NULL DEFAULT '' COMMENT '抽奖编号',
      `prize_code` varchar(64) not null default '' comment '奖品编号',
      `mobile` char(11) not null default '' comment '中奖者手机号',
      `win_time`   datetime not null default '0000-00-00 00:00:00' comment '中奖时间',
      primary key(serial),
      unique key `index_win_code` (`win_code`),
      UNIQUE KEY `index_lottery_mobile` (`lottery_code`,`mobile`)
) engine=innodb default character set utf8 comment '抽奖中奖记录表';



insert into function_info(`func_code`,`func_name`,`func_memo`,`func_url`,`item_type`,`pfunc_code`,`func_order`,`state`,`creater`,`insert_time`,`update_time`) 
values('w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz','活动管理','活动管理',null,1,null,0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('1CZ8YvtIxR3xBeziLwmTUYwp5UdoW9Hz','活动管理','活动管理','/activity/index/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('5bW84w8G8wb1Z8H7dupmooiOqXPUTxZm','活动报名管理','活动报名管理','/activity/signup/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('R3xBew8G8w5Udo7dupmooiO2Qxsztbeu','活动评论管理','活动评论管理','/activity/comment/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('z4TEhrDPSXFaf6nMoXGFsNTrrbXGYhA2','活动礼品管理','活动礼品管理','/activity/gift/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('1Z8HFaf6nMoXGFsNTr6nMoXGaix02u3l','活动总结','活动总结','/activity/summary/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('jsTZWlKcFfK5taQ4GU7z2iNG3bYiLfJK','抽奖管理','抽奖管理','/activity/lottery/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('pPlX9a4BGm8Tb9HuFoiWOWNvt4T0IGJU','奖品管理','奖品管理','/activity/prize/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('9gAahD10mKxZtzpuVaxc4t1Fgw54TQD4','中奖管理','中奖管理','/activity/winner/',0,'w6XI8PtAYm7qdIc7kpQWiAVL20KDB9zz',0,1,'root','2019-04-02 15:35:20','2019-04-02 15:35:20')


insert into role_func_info(`role_code`,`func_code`,`state`,`creater`,`insert_time`,`update_time`)
values('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','1CZ8YvtIxR3xBeziLwmTUYwp5UdoW9Hz',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','5bW84w8G8wb1Z8H7dupmooiOqXPUTxZm',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','z4TEhrDPSXFaf6nMoXGFsNTrrbXGYhA2',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','R3xBew8G8w5Udo7dupmooiO2Qxsztbeu',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','1Z8HFaf6nMoXGFsNTr6nMoXGaix02u3l',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','jsTZWlKcFfK5taQ4GU7z2iNG3bYiLfJK',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','pPlX9a4BGm8Tb9HuFoiWOWNvt4T0IGJU',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20'),
      ('xBWLQdmufqfceJIptmQmUOP81Ro0eyTH','9gAahD10mKxZtzpuVaxc4t1Fgw54TQD4',1,null,'2019-04-02 15:35:20','2019-04-02 15:35:20')

insert into attachment_file_type(`tcode`,`tname`,`tmemo`) 
values('0120','activityCover','活动宣传图'),
      ('0121','activityEditor','活动富文本编辑器'),
      ('0122','activityAttachment','活动附件'),
      ('0123','activitySummary','活动总结附件')


1
SET GLOBAL event_scheduler = ON;

2
CREATE PROCEDURE update_activity_state()
BEGIN
    IF exists (select serial from activity where  current_timestamp()=online_time) THEN
            update activity set `state`='2' where current_timestamp() = online_time;
    END IF;

    IF exists (select serial from activity where  current_timestamp()=signup_start_time) THEN
            update activity set `state`='3' where current_timestamp() = signup_start_time;
    END IF;

    IF exists (select serial from activity where  current_timestamp()=signup_end_time) THEN
            update activity set `state`='4' where current_timestamp() = signup_end_time;
    END IF;

    IF exists (select serial from activity where  current_timestamp()= activity_start_time) THEN
            update activity set `state`='5' where current_timestamp() = activity_start_time;
    END IF;

    IF exists (select serial from activity where  current_timestamp()= activity_end_time) THEN
            update activity set `state`='6' where current_timestamp() = activity_end_time;
    END IF;

    IF exists (select serial from activity where  current_timestamp()= down_time) THEN
            update activity set `state`='7' where current_timestamp() = down_time;
    END IF;
END

3
CREATE EVENT  event_update_status
ON SCHEDULE EVERY 1 second  do
begin
call update_activity_state();
end

4
ALTER EVENT event_update_status ON COMPLETION PRESERVE ENABLE;