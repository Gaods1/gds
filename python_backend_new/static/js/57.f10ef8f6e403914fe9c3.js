webpackJsonp([57],{"7YYz":function(e,t){},GrrX:function(e,t,o){"use strict";o.d(t,"c",function(){return a}),o.d(t,"a",function(){return l}),o.d(t,"d",function(){return s}),o.d(t,"b",function(){return r});var n=o("pxwZ"),i="/system/roles/",a=function(e,t){return Object(n.c)(i+e+"/",t)},l=function(e){return Object(n.d)(i,e)},s=function(e){return Object(n.b)(i,e)},r=function(e){return Object(n.a)(i+e+"/")}},ibu4:function(e,t,o){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var n=o("D4TX"),i=o("GOyC"),a=o("R5Jg"),l=o("93JQ"),s=o("pxwZ"),r="/system/account_role/",c=o("9pcb"),d=o("GrrX"),h={data:function(){var e=this;return{dialogTitle:"",accountAll:[],roleAll:[],dialogFormVisible:!1,serial:"",rules:{account:[{required:!0,message:"请输入账号",trigger:"blur"}],user_mobile:[{min:11,max:11,message:"请输入正确的手机号码",trigger:"blur"},{type:"number",message:"手机号必须为数字值",trigger:"blur"}],user_email:[{type:"email",message:"请输入正确的邮箱地址",trigger:["blur","change"]}]},currentEditLine:0,select_word:"",formData:{},handleType:"new",formOptions:{},formItems:[{prop:"account",text:"登录帐号",label:"帐号",type:"select",eleProps:{filterable:!0,placeholder:"请选择或搜索"},options:[]},{prop:"role_code",text:"角色",label:"角色",type:"select",eleProps:{filterable:!0,placeholder:"请选择角色"},options:[]},{prop:"type",text:"授权类型",label:"授权类型",type:"select",eleProps:{placeholder:"请选择授权类型"},options:[{value:1,label:"可授权权限"},{value:0,label:"可执行权限"}]},{prop:"state",text:"状态",label:"状态",type:"switch",eleProps:{"inactive-value":0,"active-value":1,"active-text":"启用","inactive-text":"不启用"}}],handleConfig:{searchTerms:[{value:"1",label:"条件一"},{value:"2",label:"条件二"},{value:"3",label:"条件三"}],newItemTxt:"分配角色",delBtn:!1,auditBtn:!1},total:0,list:[],columns:[{prop:"insert_time",label:"注册日期",align:"center",width:180},{prop:"account",label:"帐号",align:"center",width:180},{prop:"role_code",label:"角色",align:"center",width:120,formatter:function(e,t,o){return e.role}},{prop:"state",label:"状态",align:"center",width:"160",render:function(e,t){return e("el-tag",{props:{type:0===t.row.state?"danger":1===t.row.state?"success":"info"}},0===t.row.state?"禁用":1===t.row.state?"启用":"审核中")}},{prop:"type",label:"授权类型",align:"center",width:180,render:function(e,t){return e("el-tag",{props:{type:0===t.row.type?"danger":1===t.row.type?"success":"info"}},0===t.row.type?"可执行权限":1===t.row.type?"可授权权限":"未找到权限")}},{prop:"creater",label:"创建人",align:"center",width:180}],operates:{width:200,fixed:"right",list:[{label:"编辑",type:"warning",show:function(e,t){return!0},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,o){e.handleEdit(t,o)}},{label:"删除",type:"danger",icon:"el-icon-delete",show:!0,plain:!1,disabled:!1,method:function(t,o){e.handleDel(t,o)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!0}}},components:{jsonForm:l.a,curmbs:n.a,handleBox:i.a,opTable:a.a},methods:{handleSelectAccount:function(e){console.log(e)},createStateFilter:function(e){return function(t){return 0===t.value.toLowerCase().indexOf(e.toLowerCase())}},handleClose:function(e){this.$refs.formDialog.$children[0].$refs.formData.clearValidate(),e()},handleCofirm:function(e){var t,o,n,i=this;console.log(e),"edit"==this.handleType?(o=this.serial,n=e,Object(s.c)(r+o+"/",n)).then(function(e){if(e.detail)return i.$message.error(e.detail),!1;i.list.splice(i.currentEditLine,1,e),i.dialogFormVisible=!1,i.$message({type:"success",message:"编辑成功!"})}):(t=e,Object(s.d)(r,t)).then(function(e){if(e.detail)return i.$message.error(e.detail),!1;i.list.splice(0,0,e),i.dialogFormVisible=!1,i.$message({type:"success",message:"添加成功!"})})},newItem:function(){this.getAllAccount(),this.getAllRole();for(var e=0;e<this.formItems.length;e++)this.$set(this.formItems[e].eleProps,"disabled",!1),"switch"==this.formItems[e].type?this.$set(this.formData,this.formItems[e].prop,1):this.$set(this.formData,this.formItems[e].prop,"");this.dialogTitle="分配角色",this.currentEditLine=0,this.handleType="new",this.dialogFormVisible=!0},search:function(e,t){this.select_word=t,this.getList()},delAll:function(){console.log("delAll")},getAllRole:function(){var e=this;Object(d.d)({params:{page_size:"max",state:1}}).then(function(t){for(var o in console.log(t.data),e.roleAll=[],t.data){var n={};n.value=t.data[o].role_code,n.label=t.data[o].role_name,e.roleAll.push(n)}for(var i in e.formItems)"role_code"==e.formItems[i].prop&&(e.formItems[i].options=e.roleAll)})},getAllAccount:function(){var e=this;Object(c.g)({params:{admin:"True",page_size:"max",state:1}}).then(function(t){for(var o in e.accountAll=[],t.data.results){var n=t.data.results,i={};i.value=n[o].account,i.label=n[o].account,e.accountAll.push(i)}for(var a in e.formItems)"account"==e.formItems[a].prop&&(e.formItems[a].options=e.accountAll)})},getList:function(){var e,t=this;this.options.loading=!0,(e={params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}},Object(s.b)(r,e)).then(function(e){console.log("getList"),console.log(e.data.count),t.total=e.data.count,t.pagination.total=Number(e.data.count),t.list=e.data.results,t.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,console.log("handleSizeChange:"+this.pagination.pageSize),this.getList()},handleIndexChange:function(e){this.pagination=e,console.log("handleIndexChange:"+this.pagination.pageIndex),this.getList()},handleSelectionChange:function(e){console.log("val:",e)},handleEdit:function(e,t){this.getAllAccount(),this.getAllRole(),this.currentEditLine=t,this.dialogTitle="编辑",this.handleType="edit",this.serial=e.serial;for(var o=0;o<this.formItems.length;o++)void 0!==e[this.formItems[o].prop]&&(""!=e[this.formItems[o].prop]||0==e[this.formItems[o].prop]?(this.$set(this.formData,this.formItems[o].prop,e[this.formItems[o].prop]),"account"==this.formItems[o].prop&&this.$set(this.formItems[o].eleProps,"disabled",!0)):this.$set(this.formData,this.formItems[o].prop,""));console.log(this.formData),this.dialogFormVisible=!0},handleDel:function(e,t){var o=this;this.$confirm("此操作将永久删除该账户, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){var n;(n=e.serial,Object(s.a)(r+n+"/")).then(function(e){e.detail?o.$message.error(e.detail):o.list.splice(t,1)}).then(function(){o.$message({type:"success",message:"删除成功!"})})}).catch(function(){o.$message({type:"info",message:"已取消删除"})})}}},p={render:function(){var e=this,t=e.$createElement,o=e._self._c||t;return o("div",{staticClass:"warp-box"},[o("curmbs"),e._v(" "),o("div",{staticClass:"container"},[o("handleBox",{attrs:{handleConfig:e.handleConfig},on:{delAll:e.delAll,search:e.search,newItem:e.newItem}}),e._v(" "),o("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),o("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t}}},[o("jsonForm",{attrs:{handleType:e.handleType,formData:e.formData,rules:e.rules,formItems:e.formItems,formOptions:e.formOptions},on:{handleCofirm:e.handleCofirm,handleCancle:function(t){e.dialogFormVisible=!1}}})],1)],1)],1)},staticRenderFns:[]};var u=o("C7Lr")(h,p,!1,function(e){o("7YYz")},"data-v-102d868f",null);t.default=u.exports}});