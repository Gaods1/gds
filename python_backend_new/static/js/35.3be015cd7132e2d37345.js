webpackJsonp([35],{eKpW:function(e,t){},vfqV:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i=n("D4TX"),o=n("GOyC"),a=n("R5Jg"),r=n("93JQ"),l=n("8V1Y"),s=n("zo3L"),c={data:function(){var e=this;return{dialogTitle:"",accountAll:[],dialogFormVisible:!1,serial:"",rules:{dept_code:[{required:!0,message:"该项是必填项",trigger:"change"}],opinion:[{required:!0,message:"该项是必填项",trigger:"blur"}]},currentEditLine:0,select_word:"",formData:{},handleType:"new",rowData:{},formBtnList:[{label:"取消",type:"info",show:!1,icon:"",plain:!0,disabled:!1,method:"handleCancle"},{label:"提交",type:"success",icon:"",show:!0,plain:!1,disabled:!1,method:"handleIdent"}],formOptions:{labelWidth:"120px"},formItems:[{prop:"dept_code",text:"部门",label:"部门",type:"selectgroup",eleProps:{placeholder:"请选择部门"}},{prop:"result",text:"审核结果",label:"审核结果",type:"switch",eleProps:{"inactive-value":3,"active-value":2,"active-text":"通过","inactive-text":"未通过"}},{prop:"opinion",text:"审核意见",label:"审核意见",type:"input",eleProps:{type:"textarea",rows:4,placeholder:"请输入审核意见"}}],handleConfig:{searchTerms:[{value:"1",label:"条件一"},{value:"2",label:"条件二"},{value:"3",label:"条件三"}],newItemTxt:!1,delBtn:!1,auditBtn:!1},total:0,list:[],columns:[{prop:"owner_name",label:"企业名称",align:"center",width:120,formatter:function(e,t,n){if(e.owner)return e.owner.owner_name}},{prop:"owner_name_abbr",label:"企业简称",align:"center",width:120,formatter:function(e,t,n){if(e.owner)return e.owner.owner_name_abbr}},{prop:"owner_tel",label:"企业电话",align:"center",width:120,formatter:function(e,t,n){if(e.owner)return e.owner.owner_tel}},{prop:"owner_license",label:"统一社会信用代码",align:"center",width:150,formatter:function(e,t,n){if(e.owner)return e.owner.owner_license}},{prop:"state",label:"审核状态",align:"center",width:120,render:function(e,t){return e("el-tag",{props:{type:3===t.row.state?"danger":2===t.row.state?"success":"info"}},3===t.row.state?"未通过":2===t.row.state?"通过":"待审核")}},{prop:"homepage",label:"企业主页",align:"center",width:150,formatter:function(e,t,n){if(e.owner)return e.owner.homepage}},{prop:"city",label:"归属城市",align:"center",width:120,formatter:function(e,t,n){if(e.owner)return e.owner.city}},{prop:"legal_person",label:"法人姓名",align:"center",width:120,formatter:function(e,t,n){if(e.owner)return e.owner.legal_person}},{prop:"owner_mobile",label:"手机号码",align:"center",width:120,formatter:function(e,t,n){if(e.owner)return e.owner.owner_mobile}},{prop:"owner_idtype",label:"证件类型",align:"center",width:120,formatter:function(e,t,n){if(e.owner)return l.a.id_type_arr[e.owner.owner_idtype]}},{prop:"owner_id",label:"证件号码",align:"center",width:150,formatter:function(e,t,n){if(e.owner)return e.owner.owner_id}},{prop:"account",label:"关联账号",align:"center",width:120,formatter:function(e,t,n){if(e.owner)return e.owner.account}},{prop:"apply_time",label:"申请时间",align:"center",width:150,formatter:function(e,t,n){if(e.owner)return e.apply_time}}],operates:{width:200,fixed:"right",list:[{label:"详情",type:"primary",show:function(e,t){return!0},icon:"el-icon-info",plain:!0,disabled:!1,method:function(t,n){e.handleDetail(t,n)}},{label:"审核",type:"warning",show:function(e,t){return 1==t.state},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,n){e.handleCer(t,n)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!0}}},components:{jsonForm:r.a,curmbs:i.a,handleBox:o.a,opTable:a.a},methods:{handleIdent:function(){var e=this;if(!this.$refs.formData.validateForm())return!1;this.rowData.state=1==this.formData.result?3:this.formData.result,this.rowData.opinion=this.formData.opinion,this.rowData.dept_code=this.formData.dept_code,Object(s.c)(this.rowData.serial,this.rowData).then(function(t){t.detail?e.$message.error(t.detail):(e.$message({type:"success",message:"审核成功!"}),e.dialogFormVisible=!1,e.list.splice(e.currentEditLine,1))})},handleCer:function(e,t){this.dialogTitle="审核",this.handleType="cer",this.rowData=e,this.$set(this.formData,"dept_code",e.owner.dept_code),this.dialogFormVisible=!0,this.currentEditLine=t,this.$set(this.formData,"result",e.state),this.$set(this.formData,"opinion",e.opinion)},handleDetail:function(e,t){console.log(e,t),this.$router.push({name:"requirement_enterprise_apply_detail",query:{serial:e.serial}})},handleOpen:function(){this.$refs.formData.clearValidateForm(),this.$refs.formData.initSelect()},handleClose:function(e){this.$refs.formData.handleCancle(),e()},handleCofirm:function(e){var t=this;console.log(e),"edit"==this.handleType?Object(s.c)(this.serial,e).then(function(e){e.detail?t.$message.error(e.detail):(t.list.splice(t.currentEditLine,1,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"编辑成功!"}))}):Object(s.a)(e).then(function(e){e.detail?t.$message.error(e.detail):(t.list.splice(0,0,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"添加成功!"}))})},search:function(e,t){console.log("search:"+e+","+t),this.select_word=t,this.getList()},delAll:function(){console.log("delAll")},getList:function(){var e=this;this.options.loading=!0,Object(s.d)({params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}}).then(function(t){console.log(t.data.results),e.total=t.data.count,e.pagination.total=Number(t.data.count),e.list=t.data.results,e.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,console.log("handleSizeChange:"+this.pagination.pageSize),this.getList()},handleIndexChange:function(e){this.pagination=e,console.log("handleIndexChange:"+this.pagination.pageIndex),this.getList()},handleSelectionChange:function(e){console.log("val:",e)},handleEdit:function(e,t){this.currentEditLine=t,this.dialogTitle="编辑机构部门",this.handleType="edit",this.serial=e.serial;for(var n=0;n<this.formItems.length;n++)void 0!==e[this.formItems[n].prop]&&(e[this.formItems[n].prop]?(this.$set(this.formData,this.formItems[n].prop,e[this.formItems[n].prop]),"account"==this.formItems[n].prop&&this.$set(this.formItems[n].eleProps,"disabled",!0)):this.$set(this.formData,this.formItems[n].prop,""));this.dialogFormVisible=!0},handleDel:function(e,t){var n=this;this.$confirm("此操作将永久删除该账户, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){Object(s.b)(e.serial).then(function(e){e.detail?n.$message.error(e.detail):n.list.splice(t,1)}).then(function(){n.$message({type:"success",message:"删除成功!"})})}).catch(function(){n.$message({type:"info",message:"已取消删除"})})}}},d={render:function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"warp-box"},[n("curmbs"),e._v(" "),n("div",{staticClass:"container"},[n("handleBox",{attrs:{handleConfig:e.handleConfig},on:{delAll:e.delAll,search:e.search}}),e._v(" "),n("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),n("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t},opened:e.handleOpen}},[n("jsonForm",{ref:"formData",attrs:{formBtnList:e.formBtnList,handleType:e.handleType,formData:e.formData,rules:e.rules,formItems:e.formItems,formOptions:e.formOptions},on:{handleCancle:function(t){e.dialogFormVisible=!1},handleIdent:e.handleIdent}})],1)],1)],1)},staticRenderFns:[]};var h=n("C7Lr")(c,d,!1,function(e){n("eKpW")},"data-v-a289d7f4",null);t.default=h.exports},zo3L:function(e,t,n){"use strict";n.d(t,"c",function(){return a}),n.d(t,"a",function(){return r}),n.d(t,"d",function(){return l}),n.d(t,"e",function(){return s}),n.d(t,"b",function(){return c});var i=n("pxwZ"),o="/certified/requirement_enterprise_apply/",a=function(e,t){return Object(i.c)(o+e+"/",t)},r=function(e){return Object(i.d)(o,e)},l=function(e){return Object(i.b)(o,e)},s=function(e){return Object(i.b)(o+e+"/")},c=function(e){return Object(i.a)(o+e+"/")}}});