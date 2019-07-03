alter table consult_info add `update_time` datetime DEFAULT NULL COMMENT '更新时间' after insert_time;
/*征询回复表添加update_time前台按时间排序;插入和更新时都更新update_time*/
alter table consult_reply_info add `update_time` datetime default null comment '更新时间';