webpackJsonp([10],{BMLs:function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var r=a("8V1Y"),n=a("Brq+"),i={data:function(){return{defaultImg:'this.src="'+a("ZYPB")+'"',id_type_arr:r.a.id_type_arr,education_arr:r.a.education_arr,pt_type_arr:{1:"个人",2:"组合",0:"企业"},state_arr:{1:"正常",9:"暂停",99:"伪删除"},formData:{},check_show:!1,team_baseinfo:{},detailData:{},opinion:"",state:1}},created:function(){this.getDetail()},methods:{getDetail:function(){var t=this;Object(n.e)(this.$route.query.serial).then(function(e){t.team_baseinfo=e})},replaceBr:function(t){if(t)return t.replace(/\n/g,"<br/>")}}},o={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{staticClass:"detai-box"},[a("el-card",{staticClass:"box-card"},[a("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[a("span",[t._v("技术团队详情")])]),t._v(" "),a("div",{staticClass:"detail-list-box"},[a("el-form",{attrs:{"label-width":"150px"}},[a("el-form-item",{attrs:{label:"项目团队名称:"}},[t._v("\n                    "+t._s(t.team_baseinfo.pt_name)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"项目团队简称:"}},[t._v("\n                    "+t._s(t.team_baseinfo.pt_abbreviation)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"项目团队logo:"}},[a("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.team_baseinfo.logo||"{}"==t.team_baseinfo.logo?"":t.team_baseinfo.logo,onerror:t.defaultImg,alt:""}})]),t._v(" "),a("el-form-item",{attrs:{label:"团队主页url:"}},[t._v("\n                    "+t._s(t.team_baseinfo.pt_homepage)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"团队种类:"}},[t._v("\n                    "+t._s(t.pt_type_arr[t.team_baseinfo.pt_type])+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"团队城市:"}},[t._v("\n                    "+t._s(t.team_baseinfo.city)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"业务能力内部评级:"}},[t._v("\n                    "+t._s(t.team_baseinfo.pt_level)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"信用值:"}},[t._v("\n                    "+t._s(t.team_baseinfo.credit_value)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"积分:"}},[t._v("\n                    "+t._s(t.team_baseinfo.pt_integral)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"信息状态:"}},[t._v("\n                    "+t._s(t.state_arr[t.team_baseinfo.state])+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"团队领域:"}},[a("span",[t._v(t._s(t.team_baseinfo.major.join("、")))])]),t._v(" "),a("el-form-item",{attrs:{label:"团队联系人姓名:"}},[t._v("\n                    "+t._s(t.team_baseinfo.pt_people_name)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"团队联系人电话:"}},[t._v("\n                    "+t._s(t.team_baseinfo.pt_people_tel)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"证件类型:"}},[t._v("\n                    "+t._s(t.id_type_arr[t.team_baseinfo.pt_people_type])+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"证件号码:"}},[t._v("\n                    "+t._s(t.team_baseinfo.pt_people_id)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"管理人身份证正面:"}},[a("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.team_baseinfo.idfront||"{}"==t.team_baseinfo.idfront?"":t.team_baseinfo.idfront,onerror:t.defaultImg,alt:""}})]),t._v(" "),a("el-form-item",{attrs:{label:"管理人身份证背面:"}},[a("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.team_baseinfo.idback||"{}"==t.team_baseinfo.idback?"":t.team_baseinfo.idback,onerror:t.defaultImg,alt:""}})]),t._v(" "),a("el-form-item",{attrs:{label:"管理人手持身份证:"}},[a("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.team_baseinfo.idphoto||"{}"==t.team_baseinfo.idphoto?"":t.team_baseinfo.idphoto,onerror:t.defaultImg,alt:""}})]),t._v(" "),a("el-form-item",{attrs:{label:"团队宣传图片:"}},[a("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.team_baseinfo.promotional||"{}"==t.team_baseinfo.promotional?"":t.team_baseinfo.promotional,onerror:t.defaultImg,alt:""}})]),t._v(" "),a("el-form-item",{attrs:{label:"团队状态:"}},[t._v("\n                    "+t._s(t.state_arr[t.team_baseinfo.state])+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"创建时间:"}},[t._v("\n                    "+t._s(t.team_baseinfo.insert_time)+"\n                ")]),t._v(" "),a("el-form-item",{attrs:{label:"团队简介:"}},[a("span",{staticStyle:{"word-wrap":"break-word"},domProps:{innerHTML:t._s(t.replaceBr(t.team_baseinfo.pt_abstract))}})]),t._v(" "),a("el-form-item",{attrs:{label:"团队简述:"}},[a("span",{staticStyle:{"word-wrap":"break-word"},domProps:{innerHTML:t._s(t.replaceBr(t.team_baseinfo.pt_describe))}})])],1)],1)])],1)},staticRenderFns:[]};var s=a("C7Lr")(i,o,!1,function(t){a("Umgo")},"data-v-8154d862",null);e.default=s.exports},"Brq+":function(t,e,a){"use strict";a.d(e,"d",function(){return i}),a.d(e,"e",function(){return o}),a.d(e,"a",function(){return s}),a.d(e,"c",function(){return l}),a.d(e,"b",function(){return _});var r=a("pxwZ"),n="/certified/team/",i=function(t){return Object(r.b)(n,t)},o=function(t){return Object(r.b)(n+t+"/")},s=function(t){return Object(r.d)(n,t)},l=function(t,e){return Object(r.c)(n+t+"/",e)},_=function(t){return Object(r.a)(n+t+"/")}},Umgo:function(t,e){}});