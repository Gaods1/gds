webpackJsonp([56],{"45tM":function(e,t,i){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var n=i("D4TX"),o=i("GOyC"),s=i("R5Jg"),r=i("93JQ"),a=i("9pcb"),l=i("GrrX"),c={data:function(){var e=this;return{dialogTitle:"",dialogFormVisible:!1,serial:"",rules:{account:[{required:!0,message:"请输入账号",trigger:"blur"}],user_mobile:[{min:11,max:11,message:"请输入正确的手机号码",trigger:"blur"},{type:"number",message:"手机号必须为数字值",trigger:"blur"}],user_email:[{type:"email",message:"请输入正确的邮箱地址",trigger:["blur","change"]}],role_name:[{required:!0,message:"请输入角色名",trigger:"blur"}]},currentEditLine:0,select_word:"",formData:{},handleType:"new",formOptions:{labelWidth:"100px"},funcList:[],formItems:[{prop:"role_name",text:"角色名",label:"角色名",type:"input",eleProps:{placeholder:"请输入角色名称"}},{prop:"role_memo",text:"角色描述",label:"角色描述",type:"input",eleProps:{placeholder:"请输入角色描述"}},{prop:"state",text:"状态",label:"角色状态",type:"switch",eleProps:{"inactive-value":0,"active-value":1,"active-text":"启用","inactive-text":"不启用"}},{prop:"func",text:"角色功能点",label:"角色功能点",type:"select",eleProps:{filterable:!0,multiple:!0,collapseTags:!0},options:[]}],handleConfig:{searchTerms:[{value:"1",label:"条件一"},{value:"2",label:"条件二"},{value:"3",label:"条件三"}],newItemTxt:"创建角色",delBtn:!1},total:0,list:[],columns:[{prop:"role_name",label:"角色名",align:"center",width:"160"},{prop:"role_memo",label:"角色描述",align:"center",width:"160"},{prop:"state",label:"状态",align:"center",width:"80",render:function(e,t){return e("el-tag",{props:{type:0===t.row.state?"danger":1===t.row.state?"success":"info"}},0===t.row.state?"禁用":1===t.row.state?"启用":"审核中")}},{prop:"func",label:"角色功能点",align:"center",width:"160",render:function(e,t){return t.row.func.length>0?e("el-popover",{props:{placement:"right",width:"150",trigger:"click"}},[e("div",{},[t.row.func.map(function(t){return e("el-tag",{props:{size:"mini"}},t.func_name)})]),e("a",{slot:"reference",props:{plain:!0},style:{color:"#409EFF",cursor:"pointer"}},"共"+t.row.func.length+"项功能")]):e("a",{style:{color:"#409EFF",cursor:"pointer"}},"共"+t.row.func.length+"项功能")}},{prop:"insert_time",label:"注册日期",align:"center",width:180}],operates:{width:200,fixed:"right",list:[{label:"编辑",type:"warning",show:function(e,t){return!0},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,i){e.handleEdit(t,i)}},{label:"删除",type:"danger",icon:"el-icon-delete",show:!0,plain:!1,disabled:!1,method:function(t,i){e.handleDel(t,i)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!0}}},components:{jsonForm:r.a,curmbs:n.a,handleBox:o.a,opTable:s.a},methods:{getFuncList:function(){var e=this,t=localStorage.getItem("serial");Object(a.i)(t).then(function(t){for(var i in t.detail&&e.$message.error(t.detail),e.funcList=[],t.authorized_func){var n={};n.value=t.authorized_func[i].func_code,n.label=t.authorized_func[i].func_name,e.funcList.push(n)}for(var o in e.formItems)"func"==e.formItems[o].prop&&(e.formItems[o].options=e.funcList)})},handleClose:function(e){this.$refs.formDialog.$children[0].$refs.formData.clearValidate(),e()},handleCofirm:function(e){var t=this;"edit"==this.handleType?Object(l.c)(this.serial,e).then(function(e){e.detail&&t.$message.error(e.detail),t.list.splice(t.currentEditLine,1,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"编辑成功!"})}):Object(l.a)(e).then(function(e){e.detail&&t.$message.error(e.detail),t.list.splice(0,0,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"添加成功!"}),t.getList()})},newItem:function(){this.getFuncList();for(var e=0;e<this.formItems.length;e++)"switch"==this.formItems[e].type?this.$set(this.formData,this.formItems[e].prop,1):"select"==this.formItems[e].type&&1==this.formItems[e].eleProps.multiple?this.$set(this.formData,this.formItems[e].prop,[]):this.$set(this.formData,this.formItems[e].prop,"");this.dialogTitle="创建角色",this.currentEditLine=0,this.handleType="new",this.dialogFormVisible=!0},search:function(e,t){this.select_word=t,this.getList()},delAll:function(){console.log("delAll")},getList:function(){var e=this;this.options.loading=!0,Object(l.d)({params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}}).then(function(t){if(t.detail)return e.$message.error(t.detail),!1;e.total=t.count,e.pagination.total=Number(t.count),e.list=t.results,e.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,this.getList()},handleIndexChange:function(e){this.pagination=e,this.getList()},handleSelectionChange:function(e){console.log("val:",e)},handleEdit:function(e,t){this.getFuncList(),this.currentEditLine=t,this.dialogTitle="编辑角色信息",this.handleType="edit",this.serial=e.serial;for(var i=0;i<this.formItems.length;i++)if(void 0!==e[this.formItems[i].prop])if("func"==this.formItems[i].prop){this.$set(this.formData,this.formItems[i].prop,[]);for(var n=0;n<e.func.length;n++)this.$set(this.formData.func,n,e.func[n].func_code)}else e[this.formItems[i].prop]?this.$set(this.formData,this.formItems[i].prop,e[this.formItems[i].prop]):this.$set(this.formData,this.formItems[i].prop,"");this.dialogFormVisible=!0},handleDel:function(e,t){var i=this;this.$confirm("此操作将永久删除该角色, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){Object(l.b)(e.serial).then(function(e){e.detail&&i.$message.error(e.detail),i.list.splice(t,1)}).then(function(){i.$message({type:"success",message:"删除成功!"})})}).catch(function(){i.$message({type:"info",message:"已取消删除"})})}}},h={render:function(){var e=this,t=e.$createElement,i=e._self._c||t;return i("div",{staticClass:"warp-box"},[i("curmbs"),e._v(" "),i("div",{staticClass:"container"},[i("handleBox",{attrs:{handleConfig:e.handleConfig},on:{delAll:e.delAll,search:e.search,newItem:e.newItem}}),e._v(" "),i("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),i("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t}}},[i("jsonForm",{attrs:{handleType:e.handleType,formData:e.formData,rules:e.rules,formItems:e.formItems,formOptions:e.formOptions},on:{handleCofirm:e.handleCofirm,handleCancle:function(t){e.dialogFormVisible=!1}}})],1)],1)],1)},staticRenderFns:[]};var u=i("C7Lr")(c,h,!1,function(e){i("tbld")},"data-v-dee89036",null);t.default=u.exports},GrrX:function(e,t,i){"use strict";i.d(t,"c",function(){return s}),i.d(t,"a",function(){return r}),i.d(t,"d",function(){return a}),i.d(t,"b",function(){return l});var n=i("pxwZ"),o="/system/roles/",s=function(e,t){return Object(n.c)(o+e+"/",t)},r=function(e){return Object(n.d)(o,e)},a=function(e){return Object(n.b)(o,e)},l=function(e){return Object(n.a)(o+e+"/")}},tbld:function(e,t){}});