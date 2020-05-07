webpackJsonp([25],{"9W8Y":function(t,e){},egKK:function(t,e,r){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var a=r("SdNV"),i=r("A1v/"),o=r("8V1Y"),n=r("z620"),l={components:{deptGroup:a.a,detailModel:i.a},data:function(){return{verifyState:!0,formData:{},idetntForm:{dept_code:"",state:!1,opinion:""},identState:!1,rules:{dept_code:[{required:!0,message:"该项是必填项",trigger:"blur"}],opinion:[{required:!0,message:"该项是必填项",trigger:"blur"}]},formOptions:{labelWidth:"160px"},formItems:[{prop:"pt_name",text:"名称",label:"名称",type:"input"},{prop:"pt_abbreviation",text:"简称",label:"简称"},{prop:"pt_people_name",text:"联系人",label:"联系人",type:"input"},{prop:"pt_people_tel",text:"手机号码",label:"手机号码",type:"input"},{prop:"pt_homepage",text:"团队主页",label:"团队主页",type:"input"},{prop:"pt_people_type",text:"证件类型",label:"证件类型",type:"input",formatter:function(t,e){return o.a.id_type_arr[e[t]]}},{prop:"pt_people_id",text:"证件号码",label:"证件号码",type:"input"},{prop:"pt_type",text:"团队种类",label:"团队种类",type:"input",formatter:function(t,e){return o.a.project_team_arr[e[t]]}},{prop:"city",text:"归属城市",label:"归属城市",type:"input"},{prop:"major",text:"领域专业",label:"领域专业",type:"input",formatter:function(t,e){return e[t].join()}},{prop:"pt_level",text:"业务能力评级",label:"业务能力评级",type:"input"},{prop:"credit_value",text:"信用值",label:"信用值",type:"input"},{prop:"pt_integral",text:"积分",label:"积分",type:"input"},{prop:"account",text:"关联账号",label:"关联账号"},{prop:"promotional",text:"宣传图片",label:"宣传图片",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"logo-box"},[t("img",{attrs:{src:e.value.promotional}})])}},{prop:"pt_abstract",text:"简介",label:"简介",width:"100%",formatter:function(t,e){return e[t]}},{prop:"pt_describe",text:"描述",label:"描述",width:"100%",formatter:function(t,e){return e[t]}},{prop:"apply_time",text:"申请时间",label:"申请时间"},{prop:"logo",text:"LOGO",label:"LOGO",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"logo-box"},[t("img",{attrs:{src:e.value.logo}})])}},{prop:"idfront",text:"idfront",label:"身份证正面",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idfront-box"},[t("img",{attrs:{src:e.value.idfront}})])}},{prop:"idback",text:"身份证背面",label:"身份证背面",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idback-box"},[t("img",{attrs:{src:e.value.idback}})])}},{prop:"idphoto",text:"手持身份证",label:"手持身份证",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idphoto-box"},[t("img",{attrs:{src:e.value.idphoto}})])}}]}},created:function(){this.getDetail()},methods:{handleIdent:function(){var t=this;this.$refs.deptCarser.getSelected();var e="";if(this.$refs.formData.validate(function(r,a){r?e=!0:(t.$message({type:"error",message:"表单验证失败"}),e=!1)}),!e)return!1;var r={};r.state=parseInt(this.idetntForm.state),r.opinion=this.idetntForm.opinion,r.dept_code=this.idetntForm.dept_code,Object(n.a)(this.$route.query.serial,r).then(function(e){e.detail&&t.$message.error(e.detail),1!==e.state&&(t.identState=!0,t.idetntForm.state=e.state,t.idetntForm.opinion=e.opinion||"无"),t.$message({type:"success",message:"审核成功!"}),t.$router.push({path:"/team_apply"})})},initSelect:function(){this.$refs.deptCarser.init()},getDetail:function(){var t=this;Object(n.c)(this.$route.query.serial).then(function(e){e.detail&&t.$message.error(e.detail),e.team_baseinfo.apply_time=e.apply_time,t.formData=e.team_baseinfo,1!==e.state&&(t.identState=!0),t.idetntForm.opinion=e.opinion,t.idetntForm.dept_code=t.formData.dept_code||"",t.$nextTick(function(){return t.initSelect()})})}}},p={render:function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("div",{staticClass:"detai-box"},[r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header",id:"team_title"},slot:"header"},[r("span",[t._v(t._s(t.formData.pt_name+"-")+"技术团队详情")])]),t._v(" "),r("div",{staticClass:"detail-list-box"},[r("detailModel",{attrs:{formData:t.formData,formItems:t.formItems}})],1)]),t._v(" "),r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[t._v("审批意见栏")])]),t._v(" "),r("div",[r("div",{staticClass:"warper-box"},[r("el-form",{ref:"formData",attrs:{model:t.idetntForm,"label-width":"100px",disabled:t.identState,rules:t.rules}},[r("el-form-item",{attrs:{label:"部门",prop:"dept_code"}},[r("deptGroup",{ref:"deptCarser",model:{value:t.idetntForm.dept_code,callback:function(e){t.$set(t.idetntForm,"dept_code",e)},expression:"idetntForm.dept_code"}})],1),t._v(" "),r("el-form-item",{attrs:{label:"审核结果",prop:"state"}},[r("el-switch",{attrs:{"active-color":"#13ce66","inactive-color":"#ff4949","inactive-value":"3","active-value":"2","active-text":"通过","inactive-text":"未通过"},model:{value:t.idetntForm.state,callback:function(e){t.$set(t.idetntForm,"state",e)},expression:"idetntForm.state"}})],1),t._v(" "),r("el-form-item",{attrs:{label:"审核意见",prop:"opinion"}},[r("el-input",{attrs:{type:"textarea",placeholder:"请填写审批意见",rows:"6"},model:{value:t.idetntForm.opinion,callback:function(e){t.$set(t.idetntForm,"opinion",e)},expression:"idetntForm.opinion"}})],1),t._v(" "),r("el-button",{staticClass:"button",attrs:{type:"info"}},[t._v("返回")]),t._v(" "),r("el-button",{staticClass:"button",attrs:{type:"primary"},on:{click:t.handleIdent}},[t._v("提交")])],1)],1)])])],1)},staticRenderFns:[]};var s=r("C7Lr")(l,p,!1,function(t){r("9W8Y")},"data-v-0b55c2c7",null);e.default=s.exports},z620:function(t,e,r){"use strict";r.d(e,"a",function(){return o}),r.d(e,"b",function(){return n}),r.d(e,"c",function(){return l});var a=r("pxwZ"),i="/certified/team_apply/",o=function(t,e){return Object(a.c)(i+t+"/",e)},n=function(t){return Object(a.b)(i,t)},l=function(t){return Object(a.b)(i+t+"/")}}});