webpackJsonp([37],{H42Y:function(t,e,r){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var a=r("WQC0"),n=r("8V1Y"),i=r("lYIU"),o=r("1ILc"),l={components:{detailModel:a.a},data:function(){return{attach_arr:n.a.attach_arr,formData:{},idetntForm:{state:!1,broker_code:"",opinion:""},identState:!1,brokerOption:[],rules:{opinion:[{required:!0,message:"该项是必填项",trigger:"blur"}],broker_code:[{required:!0,message:"该项是必填项",trigger:"blur"}]},formOptions:{labelWidth:"160px"},formItems:[{prop:"req_name",text:"需求名称",label:"需求名称",type:"input"},{prop:"req_form_type",text:"需求类型",label:"需求类型",type:"input",formatter:function(t,e){return n.a.requirmentType_arr[e[t]]}},{prop:"state",text:"申请状态",label:"申请状态",type:"input",formatter:function(t,e){return n.a.ident_arr[e[t]]}},{prop:"apply_time",text:"申请时间",label:"申请时间",type:"input"},{prop:"mname",text:"领域专业",label:"领域专业",type:"input",formatter:function(t,e){return Array(e[t]).join()}},{prop:"Keywords",text:"关键词",label:"关键词",type:"input",formatter:function(t,e){return Array(e[t]).join()}},{prop:"username",text:"账号姓名",label:"账号姓名",type:"input"},{prop:"use_type",text:"使用方式",label:"使用方式",type:"input",formatter:function(t,e){return n.a.resultUseType_arr[e[t]]}},{prop:"obtain_type",text:"获取方式",label:"获取方式",type:"input",formatter:function(t,e){return n.a.requirementObtainType_arr[e[t]]}},{prop:"osource_name",text:"来源名称",label:"来源名称",type:"input"},{prop:"entry_type",text:"录入方式",label:"录入方式",type:"input",formatter:function(t,e){return n.a.entryType_arr[e[t]]}},{prop:"owner_type",text:"持有人类型",label:"持有人类型",type:"input",formatter:function(t,e){return n.a.ownerType_arr[e[t]]}},{prop:"Personal",text:"持有人姓名",label:"持有人姓名",type:"input"},{prop:"Enterprise",text:"持有企业名称",label:"持有企业名称",type:"input"},{prop:"owner_abstract",text:"持有人描述",label:"持有人描述",type:"input"},{prop:"cooperation_name",text:"合作方式",label:"合作方式",type:"input"},{prop:"rcoop_t_abstract",text:"合作方式描述",label:"合作方式描述",type:"input"},{prop:"expiry_dateb",text:"授权合作开始",label:"授权合作开始",type:"input"},{prop:"expiry_datee",text:"授权合作结束",label:"授权合作结束",type:"input"},{prop:"show_state",text:"需求状态",label:"需求状态",type:"input",formatter:function(t,e){return n.a.showState_arr[e[t]]}},{prop:"insert_time",text:"创建时间",label:"创建时间",type:"input"},{prop:"r_abstract",text:"需求简介",label:"需求简介",width:"100%",type:"input"},{prop:"r_abstract_detail",text:"需求详情",label:"需求详情",type:"input",width:"100%",formatter:function(t,e){return e[t]}},{prop:"Cover",text:"需求封面",label:"需求封面",type:"input",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idfront-box"},[t("img",{attrs:{src:e.value.Cover}})])}},{prop:"AgencyImg",text:"代理协议",label:"代理协议",type:"input",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idfront-box"},[t("img",{attrs:{src:e.value.AgencyImg}})])}},{prop:"PerIdFront",text:"正面照片",label:"正面照片",type:"input",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idfront-box"},[t("img",{attrs:{src:e.value.PerIdFront}})])}},{prop:"PerIdBack",text:"反面照片",label:"反面照片",type:"input",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idfront-box"},[t("img",{attrs:{src:e.value.PerIdBack}})])}},{prop:"PerHandId",text:"手持照片",label:"手持照片",type:"input",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idfront-box"},[t("img",{attrs:{src:e.value.PerHandId}})])}},{prop:"EntLicense",text:"营业执照",label:"营业执照",type:"input",render:function(t,e){return t("div",{style:{display:"inline-block"},class:"idfront-box"},[t("img",{attrs:{src:e.value.EntLicense}})])}}]}},created:function(){this.getDetail(),this.getBrokerList()},methods:{handleIdent:function(){var t=this,e="";if(this.$refs.formData.validate(function(r,a){r?e=!0:(t.$message({type:"error",message:"表单验证失败"}),e=!1)}),!e)return!1;var r={};r.state=parseInt(this.idetntForm.state),r.broker_code=this.idetntForm.broker_code,r.opinion=this.idetntForm.opinion,Object(i.a)(this.$route.query.serial,r).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;t.$message({type:"success",message:e.message}),t.$router.push({path:"/requirement_apply"})})},initSelect:function(){},getBrokerList:function(){var t=this;Object(o.d)({params:{page_size:"max"}}).then(function(e){e.detail&&t.$message.error(e.detail),t.brokerOption=[];for(var r=0;r<e.results.length;r++){var a={};a.label=e.results[r].broker_name,a.value=e.results[r].broker_code,t.brokerOption.push(a)}})},getDetail:function(){var t=this;Object(i.c)(this.$route.query.serial).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;var r=e.Requirements;r.state=e.state,r.apply_time=e.apply_time,r.opinion=e.opinion,t.formData=r,t.idetntForm.state=1!=String(e.state)?String(e.state):"3",t.idetntForm.broker_code=e.broker_code,t.idetntForm.opinion=e.opinion,1!=e.state&&(t.identState=!0)}).catch(function(t){})}}},s={render:function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("div",{staticClass:"detai-box"},[r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header",id:"result_title"},slot:"header"},[r("span",[t._v(t._s(t.formData.req_name+"-")+"详情")])]),t._v(" "),r("div",{staticClass:"detail-list-box"},[r("detailModel",{attrs:{formData:t.formData,formItems:t.formItems}}),t._v(" "),r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[t._v("附件:")])]),t._v(" "),r("el-row",t._l(t.formData.Attach,function(e,a){return r("el-col",{key:a,staticStyle:{margin:"10px"},attrs:{span:3}},[r("el-card",{attrs:{"body-style":{padding:"0px",margin:"5px"}}},[r("img",{staticClass:"image",staticStyle:{width:"100%"},attrs:{src:t.attach_arr[e.type]}}),t._v(" "),r("div",{staticStyle:{padding:"14px","text-align":"center"}},[r("span",{staticStyle:{"word-break":"beak-all","word-wrap":"break-word"}},[r("a",{staticClass:"buttonText",attrs:{href:e.look,target:"_blank"}},[t._v(t._s(e.name))])]),t._v(" "),r("div",{staticClass:"bottom clearfix"},[r("a",{staticClass:"button",attrs:{href:e.down,target:"_blank"}},[t._v("下载附件")])])])])],1)}),1)],1)]),t._v(" "),r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[t._v("审批意见栏")])]),t._v(" "),r("div",[r("div",{staticClass:"warper-box"},[r("el-form",{ref:"formData",attrs:{model:t.idetntForm,"label-width":"100px",disabled:t.identState,rules:t.rules}},[r("el-form-item",{attrs:{label:"审核结果",prop:"state"}},[r("el-switch",{attrs:{"active-color":"#13ce66","inactive-color":"#ff4949","inactive-value":"3","active-value":"2","active-text":"通过","inactive-text":"未通过"},model:{value:t.idetntForm.state,callback:function(e){t.$set(t.idetntForm,"state",e)},expression:"idetntForm.state"}})],1),t._v(" "),2==t.idetntForm.state?r("el-form-item",{attrs:{label:"技术经纪人",prop:"broker_code"}},[r("el-select",{attrs:{placeholder:"请选择或搜索"},model:{value:t.idetntForm.broker_code,callback:function(e){t.$set(t.idetntForm,"broker_code",e)},expression:"idetntForm.broker_code"}},t._l(t.brokerOption,function(t){return r("el-option",{key:t.value,attrs:{label:t.label,value:t.value}})}),1)],1):t._e(),t._v(" "),r("el-form-item",{attrs:{label:"审核意见",prop:"opinion"}},[r("el-input",{attrs:{type:"textarea",placeholder:"请填写审批意见",rows:"6"},model:{value:t.idetntForm.opinion,callback:function(e){t.$set(t.idetntForm,"opinion",e)},expression:"idetntForm.opinion"}})],1),t._v(" "),r("el-button",{staticClass:"button",attrs:{type:"info"}},[t._v("返回")]),t._v(" "),r("el-button",{staticClass:"button",attrs:{type:"primary"},on:{click:t.handleIdent}},[t._v("提交")])],1)],1)])])],1)},staticRenderFns:[]};var p=r("C7Lr")(l,s,!1,function(t){r("PVly")},"data-v-e2f66efe",null);e.default=p.exports},PVly:function(t,e){},lYIU:function(t,e,r){"use strict";r.d(e,"a",function(){return i}),r.d(e,"b",function(){return o}),r.d(e,"c",function(){return l});var a=r("pxwZ"),n="/achievement/requirement/",i=function(t,e){return Object(a.c)(n+t+"/",e)},o=function(t){return Object(a.b)(n,t)},l=function(t){return Object(a.b)(n+t+"/")}}});