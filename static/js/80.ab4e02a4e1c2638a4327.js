webpackJsonp([80],{MrOF:function(e,t){},daTO:function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var n=a("D4TX"),i=a("GOyC"),o=a("R5Jg"),l=a("93JQ"),s=a("pxwZ"),r="/consult/consult_info/",c={data:function(){var e=this;return{state_arr:{0:"待审核",1:"通过",2:"未通过",3:"发起者放弃",5:"草稿"},dialogTitle:"",dialogFormVisible:!1,serial:"",rules:{check_memo:[{required:!0,message:"请输入审核意见",trigger:"blur"},{min:1,max:500,message:"长度在 1 到 500 个字符",trigger:"blur"}]},currentEditLine:0,curentCheckRow:{},select_word:"",formData:{},handleType:"审核通过",check_type:"pass",checkData:{},formBtnList:[{label:"取消",type:"info",show:!1,icon:"",plain:!0,disabled:!1,method:"handleCancle"},{label:"提交",type:"success",icon:"",show:!0,plain:!1,disabled:!1,method:"handleIdent"}],formOptions:{},formItems:[{prop:"check_state",text:"审核结果",label:"审核结果",type:"switch",eleProps:{"inactive-value":2,"active-value":1,"active-text":"通过","inactive-text":"不通过"}},{prop:"check_memo",text:"审核意见",label:"审核意见",type:"input",eleProps:{type:"textarea",rows:4,placeholder:"请输入审核意见"}}],handleConfig:{searchTerms:[{value:"consult_title",label:"征询标题"},{value:"consult_memo",label:"征询简述"}],newItemTxt:0,delBtn:""},total:0,list:[],columns:[{prop:"consult_title",label:"标题",align:"center",width:180},{prop:"rr",label:"成果或需求",align:"center",width:120,formatter:function(e,t,a){return e.rr.join()}},{prop:"account",label:"征询人",align:"center",width:120},{prop:"consult_state",label:"状态",align:"center",width:"160",render:function(t,a){return t("el-tag",{props:{type:2===a.row.consult_state?"danger":1===a.row.consult_state?"success":"info"}},e.state_arr[a.row.consult_state])}},{prop:"consult_time",label:"开始时间",align:"center",width:160},{prop:"consult_endtime",label:"结束时间",align:"center",width:240},{prop:"insert_time",label:"创建时间",align:"center",width:180}],operates:{width:200,fixed:"right",list:[{label:"详情",type:"primary",show:function(e,t){return!0},icon:"el-icon-info",plain:!0,disabled:!1,method:function(t,a){e.handleDetail(t,a)}},{label:"审核",type:"warning",show:function(e,t){return 0==t.consult_state},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,a){e.handleCheck(t,a)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!0}}},components:{jsonForm:l.a,curmbs:n.a,handleBox:i.a,opTable:o.a},methods:{handleIdent:function(){var e,t,a=this;if(!this.$refs.formData.validateForm())return!1;this.checkData.check_state=this.formData.check_state,this.checkData.check_memo=this.formData.check_memo,this.checkData.type="check",(e=this.rowData.serial,t=this.checkData,Object(s.c)(r+e+"/",t)).then(function(e){if(0==e.state)return a.$message({type:"error",message:e.msg}),!1;a.list.splice(a.currentEditLine,1),a.dialogFormVisible=!1,a.$message({type:"success",message:"审核成功!"}),a.getList()})},handleOpen:function(){this.$set(this.formData,"check_state",0==this.curentCheckRow.check_state?2:this.curentCheckRow.check_state),this.$set(this.formData,"check_memo",this.curentCheckRow.check_memo)},handleCheck:function(e,t){this.curentCheckRow=e,this.dialogTitle="审核",this.handleType="edit",this.rowData=e,this.dialogFormVisible=!0},handleClose:function(e){this.$refs.formDialog.$children[0].$refs.formData.clearValidate(),e()},handleDetail:function(e,t){this.$router.push({name:"consult_detail",query:{serial:e.serial}})},search:function(e,t){this.select_word=t,this.getList()},getList:function(){var e,t=this;this.options.loading=!0,(e={params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}},Object(s.b)(r+"?consult_state=0",e)).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;t.total=e.count,t.pagination.total=Number(e.count),t.list=e.results,t.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,this.getList()},handleIndexChange:function(e){this.pagination=e,this.getList()},handleSelectionChange:function(e){},delAll:function(){console.log("delAll")}}},h={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"warp-box"},[a("curmbs"),e._v(" "),a("div",{staticClass:"container"},[a("handleBox",{attrs:{handleConfig:e.handleConfig},on:{delAll:e.delAll,search:e.search}}),e._v(" "),a("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),a("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t},open:e.handleOpen}},[a("jsonForm",{ref:"formData",attrs:{formBtnList:e.formBtnList,handleType:e.handleType,formData:e.formData,rules:e.rules,formItems:e.formItems,formOptions:e.formOptions},on:{handleCancle:function(t){e.dialogFormVisible=!1},handleIdent:e.handleIdent}})],1)],1)],1)},staticRenderFns:[]};var d=a("C7Lr")(c,h,!1,function(e){a("MrOF")},"data-v-4372d448",null);t.default=d.exports}});