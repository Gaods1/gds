webpackJsonp([49],{"83O/":function(t,e){},ymK5:function(t,e,r){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var a=r("cdpC"),n=r("8V1Y"),i=r("zKwF"),o={components:{detailModel:a.a},data:function(){return{formData:{},formOptions:{labelWidth:"160px"},formItems:[{prop:"ename",text:"企业名称",label:"企业名称",type:"input"},{prop:"eabbr",text:"企业简称",label:"企业简称",type:"input"},{prop:"business_license",text:"企业营业执照",label:"企业营业执照",type:"input"},{prop:"user_name",text:"关联帐号",label:"关联帐号",type:"input"},{prop:"manager_idtype",text:"法人证件类型",label:"法人证件类型",type:"input",formatter:function(t,e){return n.a.id_type_arr[e[t]]}},{prop:"manager_id",text:"法人证件号码",label:"法人证件号码",type:"input"},{prop:"manager",text:"企业联系人",label:"企业联系人",type:"input"},{prop:"emobile",text:"手机号码",label:"手机号码",type:"input"},{prop:"etel",text:"固话",label:"固话",type:"input"},{prop:"eemail",text:"邮箱",label:"邮箱",type:"input"},{prop:"homepage",text:"企业官网",label:"企业官网"},{prop:"addr",text:"企业地址",label:"企业地址"},{prop:"zipcode",text:"邮政编码",label:"邮政编码"},{prop:"elevel",text:"企业业务能力评级",label:"企业业务能力评级"},{prop:"credi_tvalue",text:"企业信用值",label:"企业信用值"},{prop:"insert_time",text:"创建时间",label:"创建时间"},{prop:"eabstract",text:"企业简介",label:"企业简介",width:"100%"},{prop:"eabstract_detail",text:"企业详情",label:"企业详情",width:"100%",formatter:function(t,e){return e[t]}}]}},created:function(){this.getDetail()},methods:{handleIdent:function(){},getDetail:function(){var t=this;Object(i.f)(this.$route.query.serial).then(function(e){t.formData=e.data})}}},l={render:function(){var t=this.$createElement,e=this._self._c||t;return e("div",{staticClass:"detai-box"},[e("el-card",{staticClass:"box-card"},[e("div",{staticClass:"clearfix",attrs:{slot:"header",id:"broker_title"},slot:"header"},[e("span",[this._v(this._s(this.formData.ename+"-")+"详情")])]),this._v(" "),e("div",{staticClass:"detail-list-box"},[e("detailModel",{attrs:{formData:this.formData,formItems:this.formItems}})],1)])],1)},staticRenderFns:[]};var p=r("C7Lr")(o,l,!1,function(t){r("83O/")},"data-v-3707a223",null);e.default=p.exports},zKwF:function(t,e,r){"use strict";r.d(e,"e",function(){return i}),r.d(e,"a",function(){return o}),r.d(e,"d",function(){return l}),r.d(e,"c",function(){return p}),r.d(e,"b",function(){return u}),r.d(e,"f",function(){return s});var a=r("pxwZ"),n="/ep/enterprise/",i=function(t){return Object(a.b)(n,t)},o=function(t){return Object(a.d)(n,t)},l=function(t,e){return Object(a.c)(n+t+"/",e)},p=function(t){return Object(a.a)(n+t+"/")},u=function(t,e){return Object(a.a)(n+t+"/",e)},s=function(t){return Object(a.b)(n+t+"/")}}});