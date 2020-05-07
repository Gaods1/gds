webpackJsonp([42],{"/vIK":function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var n=a("aA9S"),l=a.n(n),i=a("D4TX"),r=a("GOyC"),s=a("R5Jg"),o=a("IkF9"),c=a("8V1Y"),u=a("4XHg"),d=a("9pcb"),p={data:function(){var e=this;return{del_selected:[],accountAll:[],persons:[],state_arr:{1:"待审核",2:"审核通过",3:"审核不通过",4:"暂停",5:"伪删除"},dialogTitle:"",dialogFormVisible:!1,serial:"",currentEditLine:0,select_word:"",formData:{},handleType:"new",formOptions:{},formItems:[{prop:"pname",text:"个人姓名",label:"个人姓名",$default:null,type:"input",eleProps:{placeholder:"请输入个人姓名",maxlength:64},rules:[{required:!0,message:"请输入个人姓名",trigger:"change"},{min:1,max:64,message:"长度在1到64个字符",trigger:"blur"}]},{prop:"account_code",text:"关联帐号",label:"关联帐号",$default:null,type:"select",eleProps:{filterable:!0,placeholder:"请选择或搜索"},options:[]},{prop:"psex",text:"性别",label:"性别",$default:null,type:"select",eleProps:{filterable:!0,placeholder:"请选择性别"},options:[{value:1,label:"男"},{value:2,label:"女"},{value:3,label:"不详"}],rules:[{required:!0,message:"请选择性别",trigger:"change"}]},{prop:"pid_type",text:"证件类型",label:"证件类型",$default:null,type:"select",eleProps:{placeholder:"请选择证件类型"},options:[{value:1,label:"身份证"},{value:2,label:"护照"},{value:3,label:"驾照"},{value:4,label:"军官照"}],rules:[{required:!0,message:"请选择证件类型",trigger:"change"}]},{prop:"pid",text:"证件号码",label:"证件号码",$default:null,type:"input",eleProps:{placeholder:"请输入证件号码",maxlength:32},rules:[{required:!0,message:"请输入证件号码",trigger:"change"},{min:6,max:32,message:"证件号码长度6-32位",trigger:"blur"},{pattern:/^[0-9a-zA-Z]{6,32}$/,message:"请输入正确的证件号码",trigger:"blur"}]},{prop:"pmobile",text:"手机号码",label:"手机号码",$default:null,type:"input",eleProps:{placeholder:"请输入手机号码",maxlength:11},rules:[{required:!0,message:"请输入手机号码",trigger:"change"},{min:11,max:11,message:"手机号码要求11位",trigger:"blur"},{pattern:/^1[3-9]\d{9}$/,message:"请输入正确的手机号码",trigger:"blur"}]},{prop:"ptel",text:"固话",label:"固话",$default:null,type:"input",eleProps:{placeholder:"请输入固话",maxlength:14},rules:[{min:11,max:14,message:"固话要求11-14位(例:0312-0312345)",trigger:"blur"},{pattern:/^\d{3,4}-\d{7,8}$/,message:"请输入正确的固话",trigger:"blur"}]},{prop:"pemail",text:"邮箱",label:"邮箱",type:"input",eleProps:{placeholder:"请输入邮箱",maxlength:64},rules:[{required:!0,message:"请输入邮箱",trigger:"change"},{pattern:/^\w+@[a-zA-Z0-9]{2,10}(?:\.[a-z]{2,4}){1,3}$/,message:"请输入正确的邮箱地址",trigger:"blur"}]},{prop:"peducation",text:"学历",label:"学历",$default:null,type:"select",eleProps:{placeholder:"请选择学历"},options:[{value:1,label:"高中"},{value:2,label:"大专"},{value:3,label:"本科"},{value:4,label:"硕士"},{value:5,label:"博士"}],rules:[{required:!0,message:"请选择学历",trigger:"change"}]},{prop:"pabstract",text:"简介",label:"简介",$default:null,type:"input",eleProps:{placeholder:"请输入简介",type:"textarea",maxlength:500},rules:[{required:!0,message:"请输入简介",trigger:"change"}]}],handleConfig:{searchTerms:[{value:"pname",label:"个人姓名"}],newItemTxt:"创建个人信息",auditBtn:!1},total:0,list:[],columns:[{prop:"pname",label:"姓名",align:"center",width:180},{prop:"user_name",label:"关联帐号姓名",align:"center",width:180},{prop:"psex",label:"性别",align:"center",width:180,formatter:function(e,t,a){return c.a.sex_arr[e.psex]}},{prop:"pmobile",label:"手机号码",align:"center",width:120},{prop:"state",label:"状态",align:"center",width:"160",render:function(t,a){return t("el-tag",{props:{type:5===a.row.state?"danger":2===a.row.state?"success":"info"}},e.state_arr[a.row.state])}},{prop:"pid_type",label:"证件类型",align:"center",width:120,formatter:function(e,t,a){return c.a.id_type_arr[e.pid_type]}},{prop:"pid",label:"证件号码",align:"center",width:120},{prop:"ptel",label:"固话",align:"center",width:120},{prop:"pemail",label:"邮箱",align:"center",width:120},{prop:"peducation",label:"学历",align:"center",width:120,formatter:function(e,t,a){return c.a.education_arr[e.peducation]}},{prop:"insert_time",label:"创建时间",align:"center",width:180}],operates:{width:300,fixed:"right",list:[{label:"详情",type:"primary",show:function(e,t){return!0},icon:"el-icon-info",plain:!0,disabled:!1,method:function(t,a){e.handleDetail(t,a)}},{label:"编辑",type:"warning",show:function(e,t){return!0},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,a){e.handleEdit(t,a)}},{label:"删除",type:"danger",icon:"el-icon-delete",show:!0,plain:!1,disabled:!1,method:function(t,a){e.handleDel(t,a)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!0,index:!0}}},components:{jsonForm:o.a,curmbs:i.a,handleBox:r.a,opTable:s.a},methods:{handleCancle:function(){this.$refs.formData.resetForm(),this.dialogFormVisible=!1},handleClose:function(e){this.$refs.formData.resetForm(),e()},handleOpen:function(){this.$refs.formData.initSelect()},getAllAccount:function(){var e=this;Object(d.g)({params:{admin:"False",page_size:"max"}}).then(function(t){for(var a in e.accountAll=[],t.data.results){var n=t.data.results,l={};l.value=n[a].account_code,l.label=n[a].user_name,e.accountAll.push(l)}for(var i in e.formItems)"account_code"==e.formItems[i].prop&&(e.formItems[i].options=e.accountAll)})},handleCofirm:function(e){var t=this;if(!this.$refs.formData.validateForm())return!1;"edit"==this.handleType?Object(u.d)(this.serial,e).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;t.list.splice(t.currentEditLine,1,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"编辑成功!"}),t.getList()}):Object(u.a)(e).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;t.list.splice(0,0,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"添加成功!"}),t.getList()})},handleEdit:function(e,t){this.resetExtrForm(),this.getAllAccount(),this.currentEditLine=t,this.dialogTitle="编辑个人信息",this.handleType="edit",this.serial=e.serial,this.dialogFormVisible=!0,this.formData=l()({},e)},resetExtrForm:function(){var e=this;this.formItems.forEach(function(t,a){e.$set(e.formData,t.prop,t.$default),t.state&&(t.defaultList=[]),void 0!==t.defaultValue&&e.$nextTick(function(){t.defaultValue=null})})},newItem:function(){this.resetExtrForm(),this.dialogTitle="新增个人信息",this.currentEditLine=0,this.handleType="new",this.dialogFormVisible=!0,this.getAllAccount()},search:function(e,t){this.select_word=t,this.pagination.pageIndex=1,this.getList()},getList:function(){var e=this;this.options.loading=!0,Object(u.e)({params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}}).then(function(t){e.total=t.data.count,e.pagination.total=Number(t.data.count),e.list=t.data.results,e.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,this.getList()},handleIndexChange:function(e){this.pagination=e,this.getList()},handleSelectionChange:function(e){var t=new Array;for(var a in e)t.push(e[a].serial);this.del_selected=t},handleDetail:function(e,t){this.$router.push({name:"person_detail",query:{serial:e.serial}})},handleDel:function(e,t){var a=this;this.$confirm("此操作将删除该个人信息 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){Object(u.c)(e.serial).then(function(e){if(e.detail)return a.$message.error(e.detail),!1;a.list.splice(t,1)}).then(function(){a.$message({type:"success",message:"删除成功!"})})}).catch(function(){a.$message({type:"info",message:"已取消删除"})})},delAll:function(){var e=this;if(0==this.del_selected.length)return this.$message({type:"error",message:"请选择要批量删除的个人信息!"}),!1;var t=this.del_selected.shift();Object(u.b)(t,{data:this.del_selected}).then(function(t){if(t.detail)return e.$message.error(t.detail),!1;e.dialogFormVisible=!1,e.$message({type:"success",message:"批量删除成功!",duration:500,onClose:function(){window.location.reload()}})})}}},h={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"warp-box"},[a("curmbs"),e._v(" "),a("div",{staticClass:"container"},[a("handleBox",{attrs:{handleConfig:e.handleConfig},on:{delAll:e.delAll,search:e.search,newItem:e.newItem}}),e._v(" "),a("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),a("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t},opened:e.handleOpen}},[a("jsonForm",{ref:"formData",attrs:{handleType:e.handleType,formData:e.formData,formItems:e.formItems,formOptions:e.formOptions},on:{handleCancle:e.handleCancle,handleCofirm:e.handleCofirm}})],1)],1)],1)},staticRenderFns:[]};var g=a("C7Lr")(p,h,!1,function(e){a("iWbD")},"data-v-e84b21d8",null);t.default=g.exports},"4XHg":function(e,t,a){"use strict";a.d(t,"e",function(){return i}),a.d(t,"a",function(){return r}),a.d(t,"d",function(){return s}),a.d(t,"c",function(){return o}),a.d(t,"b",function(){return c}),a.d(t,"f",function(){return u});var n=a("pxwZ"),l="/ep/person/",i=function(e){return Object(n.b)(l,e)},r=function(e){return Object(n.d)(l,e)},s=function(e,t){return Object(n.c)(l+e+"/",t)},o=function(e){return Object(n.a)(l+e+"/")},c=function(e,t){return Object(n.a)(l+e+"/",t)},u=function(e){return Object(n.b)(l+e+"/")}},iWbD:function(e,t){}});