webpackJsonp([41],{HTic:function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var r=a("U4Nk"),s={components:{},data:function(){return{rm_object_type_str:{1:"技术经理人",2:"企业成果持有人",3:"个人成果持有人",4:"个人需求者",5:"企业需求者",6:"技术团队",7:"领域专家",8:"采集员"},rm_type_str:{1:"申请人已经匹配申请转化",2:"通过成果进行申请",3:"通过需求进行申请"},rm_state_str:{0:"草稿箱",1:"提交待审核",2:"审核通过",3:"审核不通过",4:"申请者放弃"},check_show:!1,detailData:!1,ruleForm:{check_state:1,check_memo:""},rules:{check_memo:[{required:!0,message:"请输入审核意见",trigger:"blur"}]}}},created:function(){this.getDetail()},computed:{},methods:{getDetail:function(){var e=this;Object(r.c)(this.$route.query.serial).then(function(t){e.detailData=t.data,1==t.data.rm_state?e.check_show=!0:e.check_show=!1}).catch(function(e){this.$message.error(e)})},check:function(){var e=this;if(this.ruleForm.check_memo){var t={};t.rm_code=this.detailData.rm_code,t.cstate=parseInt(this.ruleForm.check_state),t.cmsg=this.ruleForm.check_memo,console.info(t),Object(r.a)(this.$route.query.serial,t).then(function(t){1==t.state?(e.$message({type:"success",message:"审核成功!"}),e.$set(e.ruleForm,"check_memo",""),e.getDetail(),e.$router.go(-1)):e.$message({type:"error",message:t.msg})})}else this.$message({type:"error",message:"审核意见不能为空"})}}},i={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"detai-box"},[a("el-card",{staticClass:"box-card"},[a("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[a("span",[e._v("基本信息")])]),e._v(" "),a("div",{staticClass:"detail-list-box"},[a("el-form",{attrs:{"label-width":"120px"}},[a("el-form-item",{attrs:{label:"项目名称:"}},[e.detailData?a("span",[e._v(e._s(e.detailData.rm_title))]):e._e()]),e._v(" "),a("el-form-item",{attrs:{label:"项目主体:"}},[a("span",[e._v("\n                        "+e._s(void 0===this.rm_object_type_str[e.detailData.rm_object_type]?"不详":this.rm_object_type_str[e.detailData.rm_object_type])+"\n                    ")])]),e._v(" "),a("el-form-item",{attrs:{label:"技术经理人:"}},[e.detailData.broker_info&&e.detailData.broker_info.length>0?e._l(e.detailData.broker_info,function(t,r){return a("span",[e._v("\n                        "+e._s(t.brokerinfo.broker_name)+"\n                        "),r<e.detailData.broker_info.length-1?[e._v(",")]:e._e()],2)}):[a("span",[e._v("------")])]],2),e._v(" "),a("el-form-item",{attrs:{label:"申请类型:"}},[a("span",[e._v("\n                        "+e._s(void 0===this.rm_type_str[e.detailData.rm_type]?"不详":this.rm_type_str[e.detailData.rm_type])+"\n                    ")])]),e._v(" "),a("el-form-item",{attrs:{label:"申请状态:"}},[a("span",[e._v("\n                        "+e._s(void 0===this.rm_state_str[e.detailData.rm_state]?"不详":this.rm_state_str[e.detailData.rm_state])+"\n                    ")])]),e._v(" "),e.detailData&&e.detailData.check_info&&e.detailData.check_info.check_state?a("el-form-item",{attrs:{label:"审核意见:"}},[a("span",[e._v("\n                        "+e._s(e.detailData.check_info.check_memo)+"\n                    ")])]):e._e(),e._v(" "),a("el-form-item",{attrs:{label:"申请时间:"}},[e.detailData?a("span",[e._v(e._s(e.detailData.rm_time))]):e._e()]),e._v(" "),a("el-form-item",{attrs:{label:"创建时间:"}},[e.detailData?a("span",[e._v(e._s(e.detailData.insert_time))]):e._e()]),e._v(" "),a("el-form-item",{attrs:{label:"申请描述:"}},[e.detailData?a("span",{staticStyle:{"word-wrap":"break-word"}},[e._v(e._s(e.detailData.rm_abstract))]):e._e()]),e._v(" "),a("el-form-item",{attrs:{label:"申请详情:"}},[e.detailData?a("p",{staticStyle:{"word-wrap":"break-word"},domProps:{innerHTML:e._s(e.detailData.rm_body)}}):e._e()])],1)],1)]),e._v(" "),e.check_show?a("el-card",{staticClass:"box-card"},[a("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[a("span",[e._v("审批意见栏")])]),e._v(" "),a("div",[a("div",{staticClass:"warper-box"},[a("el-form",{ref:"ruleForm",attrs:{"label-width":"100px",model:e.ruleForm,rules:e.rules}},[a("el-form-item",{attrs:{label:"审核结果",prop:"check_state"}},[a("el-switch",{attrs:{"active-color":"#13ce66","inactive-color":"#ff4949","active-text":"审核通过","inactive-text":"审核不通过","active-value":"1","inactive-value":"-1"},model:{value:e.ruleForm.check_state,callback:function(t){e.$set(e.ruleForm,"check_state",t)},expression:"ruleForm.check_state"}})],1),e._v(" "),a("el-form-item",{attrs:{label:"审核结果",prop:"check_memo"}},[a("el-input",{attrs:{type:"textarea",placeholder:"请填写审批意见",rows:"4"},model:{value:e.ruleForm.check_memo,callback:function(t){e.$set(e.ruleForm,"check_memo",t)},expression:"ruleForm.check_memo"}})],1),e._v(" "),a("el-form-item",[a("el-button",{staticClass:"button",attrs:{type:"primary"},on:{click:e.check}},[e._v("提交\n                        ")])],1)],1)],1)])]):e._e()],1)},staticRenderFns:[]};var c=a("C7Lr")(s,i,!1,function(e){a("PCMO")},"data-v-6c8a1793",null);t.default=c.exports},PCMO:function(e,t){},U4Nk:function(e,t,a){"use strict";a.d(t,"b",function(){return i}),a.d(t,"a",function(){return c}),a.d(t,"c",function(){return l});var r=a("pxwZ"),s="/project/project_match_cer/",i=function(e){return Object(r.b)(s,e)},c=function(e,t){return Object(r.c)(s+e+"/",t)},l=function(e){return Object(r.b)(s+e+"/")}}});