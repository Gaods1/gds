webpackJsonp([14],{T0Na:function(t,e,r){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var s=r("8V1Y"),a=r("agTD"),l={data:function(){return{defaultImg:'this.src="'+r("ZYPB")+'"',id_type_arr:s.a.id_type_arr,education_arr:s.a.education_arr,type_arr:{1:"成果持有人",2:"需求持有人"},state_arr:{1:"正常",9:"暂停",99:"伪删除"},formData:{},check_show:!1,results_baseinfo:{},detailData:{},opinion:"",state:1}},created:function(){this.getDetail()},methods:{getDetail:function(){var t=this;Object(a.e)(this.$route.query.serial).then(function(e){t.results_baseinfo=e.data})},replaceBr:function(t){if(t)return t.replace(/\n/g,"<br/>")}}},n={render:function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("div",{staticClass:"detai-box"},[r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[t._v("成果持有人(企业)详情")])]),t._v(" "),r("div",{staticClass:"detail-list-box"},[r("el-form",{attrs:{"label-width":"200px"}},[r("el-form-item",{attrs:{label:"企业名称:"}},[t._v("\n                    "+t._s(t.results_baseinfo.owner_name)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"企业主页url:"}},[t._v("\n                    "+t._s(t.results_baseinfo.homepage)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"企业logo:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.results_baseinfo.logo||"{}"==t.results_baseinfo.logo?"":t.results_baseinfo.logo,onerror:t.defaultImg,alt:""}})]),t._v(" "),r("el-form-item",{attrs:{label:"企业电话:"}},[t._v("\n                    "+t._s(t.results_baseinfo.owner_tel)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"企业手机:"}},[t._v("\n                    "+t._s(t.results_baseinfo.owner_mobile)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"企业邮箱:"}},[t._v("\n                    "+t._s(t.results_baseinfo.owner_email)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"营业执照信用代码:"}},[t._v("\n                    "+t._s(t.results_baseinfo.owner_license)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"企业信用值:"}},[t._v("\n                    "+t._s(t.results_baseinfo.creditvalue)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"法人证件类型:"}},[t._v("\n                    "+t._s(t.id_type_arr[t.results_baseinfo.owner_idtype])+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"法人证件号码:"}},[t._v("\n                    "+t._s(t.results_baseinfo.owner_id)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"法人身份证正面:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.results_baseinfo.idfront||"{}"==t.results_baseinfo.idfront?"":t.results_baseinfo.idfront,onerror:t.defaultImg,alt:""}})]),t._v(" "),r("el-form-item",{attrs:{label:"法人身份证背面:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.results_baseinfo.idback||"{}"==t.results_baseinfo.idback?"":t.results_baseinfo.idback,onerror:t.defaultImg,alt:""}})]),t._v(" "),r("el-form-item",{attrs:{label:"法人手持身份证:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.results_baseinfo.idphoto||"{}"==t.results_baseinfo.idphoto?"":t.results_baseinfo.idphoto,onerror:t.defaultImg,alt:""}})]),t._v(" "),r("el-form-item",{attrs:{label:"企业宣传图片:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==t.results_baseinfo.promotional||"{}"==t.results_baseinfo.promotional?"":t.results_baseinfo.promotional,onerror:t.defaultImg,alt:""}})]),t._v(" "),r("el-form-item",{attrs:{label:"企业状态:"}},[t._v("\n                    "+t._s(t.state_arr[t.results_baseinfo.state])+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"创建时间:"}},[t._v("\n                    "+t._s(t.results_baseinfo.insert_time)+"\n                ")]),t._v(" "),r("el-form-item",{attrs:{label:"企业简介:"}},[r("span",{staticStyle:{"word-wrap":"break-word"},domProps:{innerHTML:t._s(t.replaceBr(t.results_baseinfo.owner_abstract))}})]),t._v(" "),r("el-form-item",{attrs:{label:"企业简述:"}},[r("span",{staticStyle:{"word-wrap":"break-word"},domProps:{innerHTML:t._s(t.replaceBr(t.results_baseinfo.owner_abstract_detail))}})])],1)],1)])],1)},staticRenderFns:[]};var i=r("C7Lr")(l,n,!1,function(t){r("xWge")},"data-v-dd0bc8fa",null);e.default=i.exports},agTD:function(t,e,r){"use strict";r.d(e,"d",function(){return l}),r.d(e,"e",function(){return n}),r.d(e,"a",function(){return i}),r.d(e,"c",function(){return o}),r.d(e,"b",function(){return _});var s=r("pxwZ"),a="/certified/results_enterprise/",l=function(t){return Object(s.b)(a,t)},n=function(t){return Object(s.b)(a+t+"/")},i=function(t){return Object(s.d)(a,t)},o=function(t,e){return Object(s.c)(a+t+"/",e)},_=function(t){return Object(s.a)(a+t+"/")}},xWge:function(t,e){}});