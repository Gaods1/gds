webpackJsonp([86],{"6dw0":function(t,a,e){"use strict";Object.defineProperty(a,"__esModule",{value:!0});var r=e("cdpC"),s=e("8V1Y"),i=e("f94W"),l={components:{detailModel:r.a},data:function(){var t=this;return{attach_arr:s.a.attach_arr,state_arr:{1:"可显示",0:"不可显示"},check_state_arr:{1:"审核通过",0:"未审核","-1":"审核未通过"},top_arr:{1:"置顶",0:"不置顶"},source_arr:{1:"录入",2:"爬取"},formData:{},formOptions:{labelWidth:"160px"},formItems:[{prop:"caption",text:"主标题",label:"主标题",type:"input"},{prop:"caption_ext",text:"副标题",label:"副标题",type:"input"},{prop:"group_code",text:"所属栏目",label:"所属栏目",type:"input",formatter:function(t,a){return a.group_name}},{prop:"author",text:"作者名称",label:"作者名称",type:"input"},{prop:"publisher",text:"发行单位",label:"发行单位",type:"input"},{prop:"release_date",text:"发布时间",label:"发布时间",type:"input"},{prop:"up_time",text:"上架时间",label:"上架时间",type:"input"},{prop:"down_time",text:"下架时间",label:"下架时间",type:"input"},{prop:"top_tag",text:"是否置顶",label:"是否置顶",type:"input",formatter:function(a,e){return t.top_arr[e[a]]}},{prop:"top_time",text:"置顶时间",label:"置顶时间",type:"input"},{prop:"face_pic",text:"导引图片",label:"导引图片",formatter:function(t,a){if(a[t])return'<img src="'+a.face_pic_path+a[t]+'" style="max-width:200px;max-height:120px;">'}},{prop:"state",text:"状态",label:"状态",type:"input",formatter:function(a,e){return t.state_arr[e[a]]}},{prop:"check_state",text:"审核状态",label:"审核状态",type:"input",formatter:function(a,e){return t.check_state_arr[e[a]]}},{prop:"check_time",text:"审核时间",label:"审核时间"},{prop:"source",text:"来源",label:"来源",formatter:function(a,e){return t.source_arr[e[a]]}},{prop:"district_id",text:"所属地区",label:"所属地区",formatter:function(t,a){return a.district_name}},{prop:"insert_time",text:"创建时间",label:"创建时间"},{prop:"news_body",text:"详情",label:"详情",width:"100%",formatter:function(t,a){return a[t]}}]}},created:function(){this.getDetail()},methods:{handleIdent:function(){},getDetail:function(){var t=this;Object(i.j)(this.$route.query.serial).then(function(a){t.formData=a.data})}}},n={render:function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"detai-box"},[e("el-card",{staticClass:"box-card"},[e("div",{staticClass:"clearfix",attrs:{slot:"header",id:"broker_title"},slot:"header"},[e("span",[t._v(t._s(t.formData.caption+"-")+"详情")])]),t._v(" "),e("div",{staticClass:"detail-list-box"},[e("detailModel",{attrs:{formData:t.formData,formItems:t.formItems}}),t._v(" "),e("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[e("span",[t._v("附件:")])]),t._v(" "),e("el-row",[t._l(t.formData.attach1,function(a,r){return e("el-col",{key:r,staticStyle:{margin:"10px"},attrs:{span:3}},[e("el-card",{attrs:{"body-style":{padding:"0px",margin:"5px"}}},[e("img",{staticClass:"image",staticStyle:{width:"100%"},attrs:{src:t.attach_arr[a.type]}}),t._v(" "),e("div",{staticStyle:{padding:"14px","text-align":"center"}},[e("span",{staticStyle:{"word-break":"beak-all","word-wrap":"break-word"}},[e("a",{staticClass:"buttonText",attrs:{href:a.look,target:"_blank"}},[t._v(t._s(a.file_caption))])]),t._v(" "),e("div",{staticClass:"bottom clearfix"},[e("a",{staticClass:"button",attrs:{href:a.down,target:"_blank"}},[t._v("下载附件")])])])])],1)}),t._v(" "),t._l(t.formData.attach2,function(a,r){return e("el-col",{key:r,staticStyle:{margin:"10px"},attrs:{span:3}},[e("el-card",{attrs:{"body-style":{padding:"0px",margin:"5px"}}},[e("img",{staticClass:"image",staticStyle:{width:"100%"},attrs:{src:t.attach_arr[a.type]}}),t._v(" "),e("div",{staticStyle:{padding:"14px","text-align":"center"}},[e("span",{staticStyle:{"word-break":"beak-all","word-wrap":"break-word"}},[e("a",{staticClass:"buttonText",attrs:{href:a.look,target:"_blank"}},[t._v(t._s(a.file_caption))])]),t._v(" "),e("div",{staticClass:"bottom clearfix"},[e("a",{staticClass:"button",attrs:{href:a.down,target:"_blank"}},[t._v("下载附件")])])])])],1)}),t._v(" "),t._l(t.formData.attach3,function(a,r){return e("el-col",{key:r,staticStyle:{margin:"10px"},attrs:{span:3}},[e("el-card",{attrs:{"body-style":{padding:"0px",margin:"5px"}}},[e("img",{staticClass:"image",staticStyle:{width:"100%"},attrs:{src:t.attach_arr[a.type]}}),t._v(" "),e("div",{staticStyle:{padding:"14px","text-align":"center"}},[e("span",{staticStyle:{"word-break":"beak-all","word-wrap":"break-word"}},[e("a",{staticClass:"buttonText",attrs:{href:a.look,target:"_blank"}},[t._v(t._s(a.file_caption))])]),t._v(" "),e("div",{staticClass:"bottom clearfix"},[e("a",{staticClass:"button",attrs:{href:a.down,target:"_blank"}},[t._v("下载附件")])])])])],1)}),t._v(" "),t._l(t.formData.attach4,function(a,r){return e("el-col",{key:r,staticStyle:{margin:"10px"},attrs:{span:3}},[e("el-card",{attrs:{"body-style":{padding:"0px",margin:"5px"}}},[e("img",{staticClass:"image",staticStyle:{width:"100%"},attrs:{src:t.attach_arr[a.type]}}),t._v(" "),e("div",{staticStyle:{padding:"14px","text-align":"center"}},[e("span",{staticStyle:{"word-break":"beak-all","word-wrap":"break-word"}},[e("a",{staticClass:"buttonText",attrs:{href:a.look,target:"_blank"}},[t._v(t._s(a.file_caption))])]),t._v(" "),e("div",{staticClass:"bottom clearfix"},[e("a",{staticClass:"button",attrs:{href:a.down,target:"_blank"}},[t._v("下载附件")])])])])],1)}),t._v(" "),t._l(t.formData.attach5,function(a,r){return e("el-col",{key:r,staticStyle:{margin:"10px"},attrs:{span:3}},[e("el-card",{attrs:{"body-style":{padding:"0px",margin:"5px"}}},[e("img",{staticClass:"image",staticStyle:{width:"100%"},attrs:{src:t.attach_arr[a.type]}}),t._v(" "),e("div",{staticStyle:{padding:"14px","text-align":"center"}},[e("span",{staticStyle:{"word-break":"beak-all","word-wrap":"break-word"}},[e("a",{staticClass:"buttonText",attrs:{href:a.look,target:"_blank"}},[t._v(t._s(a.file_caption))])]),t._v(" "),e("div",{staticClass:"bottom clearfix"},[e("a",{staticClass:"button",attrs:{href:a.down,target:"_blank"}},[t._v("下载附件")])])])])],1)})],2)],1)])],1)},staticRenderFns:[]};var o=e("C7Lr")(l,n,!1,function(t){e("pHVh")},"data-v-1a555050",null);a.default=o.exports},pHVh:function(t,a){}});