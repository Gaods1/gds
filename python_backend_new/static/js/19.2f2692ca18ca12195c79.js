webpackJsonp([19],{5520:function(e,t,r){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var s=r("8V1Y"),a=r("FnNf"),n={data:function(){return{defaultImg:'this.src="'+r("ZYPB")+'"',id_type_arr:s.a.id_type_arr,education_arr:s.a.education_arr,type_arr:{1:"成果持有企业",2:"需求持有企业"},state_arr:{1:"正常",9:"暂停",99:"伪删除"},formData:{},check_show:!1,results_baseinfo:{},detailData:{},opinion:"",state:1}},created:function(){this.getDetail()},methods:{getDetail:function(){var e=this;Object(a.e)(this.$route.query.serial).then(function(t){e.results_baseinfo=t})},replaceBr:function(e){if(e)return e.replace(/\n/g,"<br/>")}}},l={render:function(){var e=this,t=e.$createElement,r=e._self._c||t;return r("div",{staticClass:"detai-box",attrs:{id:"detai-box"}},[r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[e._v("需求持有企业详情")])]),e._v(" "),r("div",{staticClass:"detail-list-box"},[r("el-form",{ref:"results_baseinfo",attrs:{"label-width":"140px",model:e.results_baseinfo}},[r("el-form-item",{attrs:{label:"企业名称:"}},[r("span",{model:{value:e.results_baseinfo.owner_name,callback:function(t){e.$set(e.results_baseinfo,"owner_name",t)},expression:"results_baseinfo.owner_name"}},[e._v(e._s(e.results_baseinfo.owner_name))])]),e._v(" "),r("el-form-item",{attrs:{label:"企业简称:"}},[e._v("\n                    "+e._s(e.results_baseinfo.owner_name_abbr)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"企业logo:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==e.results_baseinfo.logo||"{}"==e.results_baseinfo.logo?"":e.results_baseinfo.logo,onerror:e.defaultImg,alt:""}})]),e._v(" "),r("el-form-item",{attrs:{label:"企业主页url:"}},[e._v("\n                    "+e._s(e.results_baseinfo.homepage)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"企业电话:"}},[e._v("\n                    "+e._s(e.results_baseinfo.owner_tel)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"企业手机:"}},[e._v("\n                    "+e._s(e.results_baseinfo.owner_mobile)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"企业邮箱:"}},[e._v("\n                    "+e._s(e.results_baseinfo.owner_email)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"营业社会信用代码:"}},[e._v("\n                    "+e._s(e.results_baseinfo.owner_license)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"归属城市:"}},[e._v("\n                    "+e._s(e.results_baseinfo.city)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"所属领域:"}},e._l(e.results_baseinfo.major,function(t,s){return r("span",{key:s},[e._v("\n                        "+e._s(t)+"\n                    ")])}),0),e._v(" "),r("el-form-item",{attrs:{label:"企业信用值:"}},[e._v("\n                    "+e._s(e.results_baseinfo.creditvalue)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"企业法人:"}},[e._v("\n                    "+e._s(e.results_baseinfo.legal_person)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"法人证件类型:"}},[e._v("\n                    "+e._s(e.id_type_arr[e.results_baseinfo.owner_idtype])+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"法人证件号码:"}},[e._v("\n                    "+e._s(e.results_baseinfo.owner_id)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"法人身份证正面:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==e.results_baseinfo.idfront||"{}"==e.results_baseinfo.idfront?"":e.results_baseinfo.idfront,onerror:e.defaultImg,alt:""}})]),e._v(" "),r("el-form-item",{attrs:{label:"法人身份证反面:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==e.results_baseinfo.idback||"{}"==e.results_baseinfo.idback?"":e.results_baseinfo.idback,onerror:e.defaultImg,alt:""}})]),e._v(" "),r("el-form-item",{attrs:{label:"法人手持身份证:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==e.results_baseinfo.idphoto||"{}"==e.results_baseinfo.idphoto?"":e.results_baseinfo.idphoto,onerror:e.defaultImg,alt:""}})]),e._v(" "),r("el-form-item",{attrs:{label:"营业执照:"}},[r("img",{staticStyle:{width:"100px",height:"100px"},attrs:{src:null==e.results_baseinfo.license||"{}"==e.results_baseinfo.license?"":e.results_baseinfo.license,onerror:e.defaultImg,alt:""}})]),e._v(" "),r("el-form-item",{attrs:{label:"企业状态:"}},[e._v("\n                    "+e._s(e.state_arr[e.results_baseinfo.state])+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"创建时间:"}},[e._v("\n                    "+e._s(e.results_baseinfo.insert_time)+"\n                ")]),e._v(" "),r("el-form-item",{attrs:{label:"企业简介:"}},[r("span",{staticStyle:{"word-wrap":"break-word"},domProps:{innerHTML:e._s(e.replaceBr(e.results_baseinfo.owner_abstract))}})]),e._v(" "),r("el-form-item",{attrs:{label:"企业简述:"}},[r("span",{staticStyle:{"word-wrap":"break-word"},domProps:{innerHTML:e._s(e.replaceBr(e.results_baseinfo.owner_abstract_detail))}})])],1)],1)])],1)},staticRenderFns:[]};var i=r("C7Lr")(n,l,!1,function(e){r("u9gY")},"data-v-6e0970f6",null);t.default=i.exports},FnNf:function(e,t,r){"use strict";r.d(t,"d",function(){return n}),r.d(t,"e",function(){return l}),r.d(t,"a",function(){return i}),r.d(t,"c",function(){return o}),r.d(t,"b",function(){return _});var s=r("pxwZ"),a="/certified/requirement_enterprise/",n=function(e){return Object(s.b)(a,e)},l=function(e){return Object(s.b)(a+e+"/")},i=function(e){return Object(s.d)(a,e)},o=function(e,t){return Object(s.c)(a+e+"/",t)},_=function(e){return Object(s.a)(a+e+"/")}},u9gY:function(e,t){}});