webpackJsonp([48],{GSGY:function(e,t){},"nT+g":function(e,t,l){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var a=l("aA9S"),n=l.n(a),r=l("D4TX"),i=l("GOyC"),s=l("R5Jg"),o=l("IkF9"),u=l("8V1Y"),p=l("zKwF"),d=l("9pcb"),c={data:function(){var e=this;return{del_selected:[],accountAll:[],state_arr:{1:"待审核",2:"审核通过",3:"审核不通过",4:"暂停",5:"伪删除"},dialogTitle:"",enterprises:[],dialogFormVisible:!1,serial:"",currentEditLine:0,select_word:"",formData:{},handleType:"new",formOptions:{labelWidth:"200px"},formItems:[{prop:"ename",text:"企业名称",label:"企业名称",$default:null,type:"input",eleProps:{placeholder:"请输入企业名称",maxlength:64},rules:[{required:!0,message:"请输入企业名称",trigger:"change"},{min:1,max:64,message:"长度在1到64个字符",trigger:"blur"}]},{prop:"account_code",text:"关联帐号",label:"关联帐号",$default:null,type:"select",eleProps:{filterable:!0,placeholder:"请选择或搜索"},options:[]},{prop:"eabbr",text:"企业简称",label:"企业简称",$default:null,type:"input",eleProps:{maxlength:32,placeholder:"请输入企业简称"},rules:[{required:!0,message:"请输入企业简称",trigger:"change"},{min:1,max:32,message:"长度在1到32个字符",trigger:"blur"}]},{prop:"business_license",text:"企业营业执照",label:"企业营业执照",$default:null,type:"input",eleProps:{maxlength:32,placeholder:"请输入企业营业执照"},rules:[{required:!0,message:"请输入企业营业执照",trigger:"change"},{min:1,max:32,message:"长度在1到32个字符",trigger:"blur"}]},{prop:"manager",text:"企业联系人",label:"企业联系人",$default:null,type:"input",eleProps:{maxlength:16,placeholder:"请输入企业联系人"},rules:[{required:!0,message:"请输入企业联系人",trigger:"change"},{min:1,max:16,message:"长度在1到16个字符",trigger:"blur"}]},{prop:"homepage",text:"企业官网",label:"企业官网",$default:null,type:"input",eleProps:{maxlength:75,placeholder:"请输入企业官网"},rules:[{pattern:/^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,message:"企业官网url不正确",trigger:"blur"}]},{prop:"emobile",text:"手机号码",label:"手机号码",$default:null,type:"input",eleProps:{placeholder:"请输入手机号码",maxlength:11},rules:[{required:!0,message:"请输入手机号码",trigger:"change"},{pattern:/^1[3-9]\d{9}$/,message:"请输入正确的手机号码",trigger:"blur"}]},{prop:"etel",text:"固话",label:"固话",$default:null,type:"input",eleProps:{placeholder:"请输入固话",maxlength:14},rules:[{min:11,max:14,message:"固话要求11-14位(例:0312-0312345)",trigger:"blur"},{pattern:/^\d{3,4}-\d{7,8}$/,message:"请输入正确的固话",trigger:"blur"}]},{prop:"eemail",text:"邮箱",label:"邮箱",$default:null,type:"input",eleProps:{placeholder:"请输入邮箱",maxlength:64},rules:[{pattern:/^\w+@[a-zA-Z0-9]{2,10}(?:\.[a-z]{2,4}){1,3}$/,message:"请输入正确的邮箱地址",trigger:"blur"}]},{prop:"addr",text:"企业地址",label:"企业地址",$default:null,type:"input",eleProps:{placeholder:"请输入企业地址",maxlength:255}},{prop:"zipcode",text:"企业邮编",label:"企业邮编",$default:null,type:"input",eleProps:{placeholder:"请输入企业邮编",maxlength:8}},{prop:"elevel",text:"企业业务能力评级(1-5)",label:"企业业务能力评级(1-5)",$default:null,type:"input",eleProps:{placeholder:"请输入企业业务能力评级(1-5)",maxlength:1},rules:[{pattern:/^[1,2,3,4,5]$/,message:"请输入企业业务能力评级(1-5)",trigger:"blur"}]},{prop:"credi_tvalue",text:"企业信用值",label:"企业信用值(1-100)",$default:null,type:"input",eleProps:{placeholder:"请输入企业信用值(1-100)",maxlength:3},rules:[{pattern:/^([1-9]|([1-9]\d)|100)$/,message:"请输入企业信用值(1-100)",trigger:"blur"}]},{prop:"manager_idtype",text:"法人证件类型",label:"法人证件类型",$$default:null,type:"select",eleProps:{placeholder:"请选择证件类型"},options:[{value:1,label:"身份证"},{value:2,label:"护照"},{value:3,label:"驾照"},{value:4,label:"军官照"}],rules:[{required:!0,message:"请选择证件类型",trigger:"change"}]},{prop:"manager_id",text:"法人证件号码",label:"法人证件号码",$default:null,type:"input",eleProps:{placeholder:"请输入法人证件号码",maxlength:32},rules:[{required:!0,message:"请输入法人证件号码",trigger:"change"},{min:6,max:32,message:"证件号码长度6-32位",trigger:"blur"},{pattern:/^[0-9a-zA-Z]{6,32}$/,message:"请输入正确的证件号码",trigger:"blur"}]},{prop:"eabstract",text:"企业简述",label:"企业简述",$default:null,type:"input",eleProps:{placeholder:"请输入企业简述",type:"textarea",maxlength:500},rules:[{required:!0,message:"请输入企业简述",trigger:"change"}]},{prop:"eabstract_detail",text:"企业描述",label:"企业描述",$default:null,type:"editor",defaultValue:"",apiUrl:"",eleProps:{maxlength:65535}}],handleConfig:{searchTerms:[{value:"ename",label:"企业名称"}],newItemTxt:"创建企业信息",auditBtn:!1},total:0,list:[],columns:[{prop:"ename",label:"企业名称",align:"center",width:180},{prop:"user_name",label:"关联帐号姓名",align:"center",width:180},{prop:"eabbr",label:"企业简称",align:"center",width:180},{prop:"business_license",label:"企业营业执照",align:"center",width:120},{prop:"state",label:"状态",align:"center",width:"160",render:function(t,l){return t("el-tag",{props:{type:5===l.row.state?"danger":2===l.row.state?"success":"info"}},e.state_arr[l.row.state])}},{prop:"manager_idtype",label:"法人证件类型",align:"center",width:120,formatter:function(e,t,l){return u.a.id_type_arr[e.manager_idtype]}},{prop:"manager_id",label:"法人证件号码",align:"center",width:120},{prop:"manager",label:"企业联系人",align:"center",width:120},{prop:"emobile",label:"手机号码",align:"center",width:120},{prop:"etel",label:"固话",align:"center",width:120},{prop:"eemail",label:"邮箱",align:"center",width:120},{prop:"addr",label:"企业地址",align:"center",width:120},{prop:"elevel",label:"企业业务能力评级",align:"center",width:180},{prop:"credi_tvalue",label:"企业信用值",align:"center",width:180},{prop:"insert_time",label:"创建时间",align:"center",width:180}],operates:{width:300,fixed:"right",list:[{label:"详情",type:"primary",show:function(e,t){return!0},icon:"el-icon-info",plain:!0,disabled:!1,method:function(t,l){e.handleDetail(t,l)}},{label:"编辑",type:"warning",show:function(e,t){return!0},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,l){e.handleEdit(t,l)}},{label:"删除",type:"danger",icon:"el-icon-delete",show:!0,plain:!1,disabled:!1,method:function(t,l){e.handleDel(t,l)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!0,index:!0}}},components:{jsonForm:o.a,curmbs:r.a,handleBox:i.a,opTable:s.a},methods:{handleCancle:function(){this.$refs.formData.resetForm(),this.dialogFormVisible=!1},handleClose:function(e){this.$refs.formData.resetForm(),e()},handleOpen:function(){this.$refs.formData.initSelect()},handleCofirm:function(e){var t=this;if(!this.$refs.formData.validateForm())return!1;"edit"==this.handleType?Object(p.d)(this.serial,e).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;t.list.splice(t.currentEditLine,1,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"编辑成功!"}),t.getList()}):Object(p.a)(e).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;t.list.splice(0,0,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"添加成功!"}),t.getList()})},handleEdit:function(e,t){var l=this;this.resetExtrForm(),this.getAllAccount(),this.currentEditLine=t,this.dialogTitle="编辑企业信息",this.handleType="edit",this.serial=e.serial,this.dialogFormVisible=!0,this.formData=n()({},e),this.formItems.forEach(function(t,a){void 0!==t.defaultValue&&l.$nextTick(function(){l.$set(t,"defaultValue",e[t.prop])})})},resetExtrForm:function(){var e=this;this.formItems.forEach(function(t,l){e.$set(e.formData,t.prop,t.$default),t.state&&(t.defaultList=[]),void 0!==t.defaultValue&&e.$nextTick(function(){t.defaultValue=null})})},getAllAccount:function(){var e=this;Object(d.g)({params:{admin:"False",page_size:"max"}}).then(function(t){for(var l in t.detail&&e.$message.error(t.detail),e.accountAll=[],t.results){var a=t.results,n={};n.value=a[l].account_code,n.label=a[l].user_name,e.accountAll.push(n)}for(var r in e.formItems)"account_code"==e.formItems[r].prop&&(e.formItems[r].options=e.accountAll)})},newItem:function(){this.resetExtrForm(),this.dialogTitle="新增企业信息",this.currentEditLine=0,this.handleType="new",this.dialogFormVisible=!0,this.getAllAccount()},search:function(e,t){this.select_word=t,this.pagination.pageIndex=1,this.getList()},getList:function(){var e=this;this.options.loading=!0,Object(p.e)({params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}}).then(function(t){t.detail&&e.$message.error(t.detail),e.total=t.count,e.pagination.total=Number(t.count),e.list=t.results,e.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,this.getList()},handleIndexChange:function(e){this.pagination=e,this.getList()},handleSelectionChange:function(e){var t=new Array;for(var l in e)t.push(e[l].serial);this.del_selected=t},handleDetail:function(e,t){this.$router.push({name:"enterprise_detail",query:{serial:e.serial}})},handleDel:function(e,t){var l=this;this.$confirm("此操作将删除该企业信息 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){Object(p.c)(e.serial).then(function(e){l.list.splice(t,1)}).then(function(){l.$message({type:"success",message:"删除成功!"})})}).catch(function(){l.$message({type:"info",message:"已取消删除"})})},delAll:function(){var e=this;if(0==this.del_selected.length)return this.$message({type:"error",message:"请选择要批量删除的企业信息!"}),!1;var t=this.del_selected.shift();Object(p.b)(t,{data:this.del_selected}).then(function(t){if(t.detail)return e.$message.error(t.detail),!1;e.dialogFormVisible=!1,e.$message({type:"success",message:"批量删除成功!",duration:500,onClose:function(){window.location.reload()}})})}}},g={render:function(){var e=this,t=e.$createElement,l=e._self._c||t;return l("div",{staticClass:"warp-box"},[l("curmbs"),e._v(" "),l("div",{staticClass:"container"},[l("handleBox",{attrs:{handleConfig:e.handleConfig},on:{delAll:e.delAll,search:e.search,newItem:e.newItem}}),e._v(" "),l("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),l("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t},opened:e.handleOpen}},[l("jsonForm",{ref:"formData",attrs:{handleType:e.handleType,formData:e.formData,formItems:e.formItems,formOptions:e.formOptions},on:{handleCancle:e.handleCancle,handleCofirm:e.handleCofirm}})],1)],1)],1)},staticRenderFns:[]};var h=l("C7Lr")(c,g,!1,function(e){l("GSGY")},"data-v-4ee20dbc",null);t.default=h.exports},zKwF:function(e,t,l){"use strict";l.d(t,"e",function(){return r}),l.d(t,"a",function(){return i}),l.d(t,"d",function(){return s}),l.d(t,"c",function(){return o}),l.d(t,"b",function(){return u}),l.d(t,"f",function(){return p});var a=l("pxwZ"),n="/ep/enterprise/",r=function(e){return Object(a.b)(n,e)},i=function(e){return Object(a.d)(n,e)},s=function(e,t){return Object(a.c)(n+e+"/",t)},o=function(e){return Object(a.a)(n+e+"/")},u=function(e,t){return Object(a.a)(n+e+"/",t)},p=function(e){return Object(a.b)(n+e+"/")}}});