webpackJsonp([66],{JNgn:function(e,t,i){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var a=i("a3Yh"),n=i.n(a),s=i("aA9S"),l=i.n(s),r=i("D4TX"),o=i("GOyC"),c=i("R5Jg"),d=i("IkF9"),h=(i("8V1Y"),i("k5wd")),f={data:function(){var e=this;return{activity_arr:[],del_selected:[],state_arr:{0:"伪删除",1:"正常",2:"禁用"},dialogTitle:"",dialogFormVisible:!1,serial:"",currentEditLine:0,select_word:"",formData:{},handleType:"new",formOptions:{labelWidth:"250px"},formItems:[{prop:"activity_code",text:"活动",label:"活动",$default:null,type:"select",eleProps:{filterable:!0,placeholder:"请选择添加礼品的活动"},options:[],rules:[{required:!0,message:"请选择添加礼品的活动",trigger:"change"}]},{prop:"gift_name",text:"活动礼品名称",label:"活动礼品名称",$default:null,type:"input",eleProps:{placeholder:"活动礼品名称",maxlength:32},rules:[{required:!0,message:"请填写活动礼品名称",trigger:"change"},{min:1,max:32,message:"活动礼品名称长度在1到32个字符",trigger:"blur"}]},{prop:"gift_abstract",text:"活动礼品描述",label:"活动礼品描述",$default:null,type:"editor",defaultValue:"",apiUrl:"",imageShow:!1,eleProps:{maxlength:255},rules:[{required:!0,message:"请填写活动礼品描述",trigger:"change"}]},{prop:"state",text:"状态",label:"状态",$default:null,type:"select",eleProps:{filterable:!0,placeholder:"请选择状态"},options:[{value:0,label:"伪删除"},{value:1,label:"正常"},{value:2,label:"禁用"}],rules:[{required:!0,message:"请选择状态",trigger:"change"}]}],handleConfig:{searchTerms:[{value:"gift_name",label:"礼品名称"}],newItemTxt:"创建活动的礼品",auditBtn:!1},total:0,list:[],columns:[{prop:"activity_title",label:"活动标题",align:"center",width:180},{prop:"gift_name",label:"礼品名称",align:"center",width:180},{prop:"state",label:"状态",align:"center",width:"160",render:function(t,i){return t("el-tag",{props:{type:2===i.row.state?"danger":1===i.row.state?"success":"info"}},e.state_arr[i.row.state])}},{prop:"gift_abstract",label:"活动礼品描述",align:"center",width:180,formatter:function(e,t,i){return e.gift_abstract}},{prop:"insert_time",label:"创建时间",align:"center",width:180}],operates:{width:300,fixed:"right",list:[{label:"编辑",type:"warning",show:function(e,t){return!0},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,i){e.handleEdit(t,i)}},{label:"删除",type:"danger",icon:"el-icon-delete",show:!0,plain:!1,disabled:!1,method:function(t,i){e.handleDel(t,i)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!0,index:!0}}},components:{jsonForm:d.a,curmbs:r.a,handleBox:o.a,opTable:c.a},methods:{handleCancle:function(){this.$refs.formData.resetForm(),this.dialogFormVisible=!1},handleClose:function(e){this.$refs.formData.resetForm(),e()},handleOpen:function(){this.$refs.formData.initSelect()},handleCofirm:function(e){var t=this;if(!this.$refs.formData.validateForm())return!1;console.log(e),"edit"==this.handleType?Object(h.x)(this.serial,e).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;t.list.splice(t.currentEditLine,1,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"编辑成功!"}),t.getList()}):Object(h.c)(e).then(function(e){if(e.detail)return t.$message.error(e.detail),!1;t.list.splice(0,0,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"添加成功!"}),t.getList()})},handleEdit:function(e,t){var i=this;this.resetExtrForm(),this.getAllActivity(),this.currentEditLine=t,this.dialogTitle="编辑活动的礼品",this.handleType="edit",this.serial=e.serial,this.dialogFormVisible=!0,this.formData=l()({},e),this.formItems.forEach(function(t,a){t.state&&e[t.prop]&&("picture"!==t.listType?i.forMataAttachList(t.state,i.formData[t.prop],a):i.forMataFileList(t.state,i.formData.face_pic,a)),void 0!==t.defaultValue&&i.$nextTick(function(){i.$set(t,"defaultValue",e[t.prop])})})},forMataAttachList:function(e,t,i){var a=this;if(this.formItems[i].defaultList=[],t.length)for(var s=function(s){var l={};l.response="attachment"==e?n()({},e,[t[s].down]):n()({},e,t[s].down),l.status="success",l.file_caption=t[s].file_caption,l.percentage="100",a.$nextTick(function(){a.formItems[i].defaultList.push(l)})},l=0;l<t.length;l++)s(l)},forMataFileList:function(e,t,i){var a=this,s={};s.response=n()({},e,t),s.status="success",s.percentage="100",this.$nextTick(function(){a.formItems[i].defaultList.splice(0,1,s)})},resetExtrForm:function(){var e=this;this.formItems.forEach(function(t,i){e.$set(e.formData,t.prop,t.$default),t.state&&(t.defaultList=[]),void 0!==t.defaultValue&&e.$nextTick(function(){t.defaultValue=null})})},getAllActivity:function(){var e=this;Object(h.C)({params:{pageSize:"max"}}).then(function(t){for(var i in t.detail&&e.$message.error(t.detail),e.activity_arr=[],t.results)e.activity_arr.push({value:t.results[i].activity_code,label:t.results[i].activity_title});for(var i in e.formItems)"activity_code"==e.formItems[i].prop&&e.$set(e.formItems[i],"options",e.activity_arr)})},newItem:function(){this.resetExtrForm(),this.dialogTitle="新增活动的礼品",this.currentEditLine=0,this.handleType="new",this.dialogFormVisible=!0,this.getAllActivity()},search:function(e,t){this.select_word=t,this.pagination.pageIndex=1,this.getList()},getList:function(){var e=this;this.options.loading=!0,Object(h.F)({params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}}).then(function(t){t.detail&&e.$message.error(t.detail),e.total=t.count,e.pagination.total=Number(t.count),e.list=t.results,e.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,this.getList()},handleIndexChange:function(e){this.pagination=e,this.getList()},handleSelectionChange:function(e){var t=new Array;for(var i in e)t.push(e[i].serial);this.del_selected=t},handleDel:function(e,t){var i=this;this.$confirm("此操作将删除该活动的礼品是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){Object(h.q)(e.serial).then(function(e){i.list.splice(t,1)}).then(function(){i.$message({type:"success",message:"删除成功!"})})}).catch(function(){i.$message({type:"info",message:"已取消删除"})})},delAll:function(){var e=this;if(0==this.del_selected.length)return this.$message({type:"error",message:"请选择要批量删除的活动礼品!"}),!1;var t=this.del_selected.shift();Object(h.k)(t,{data:this.del_selected}).then(function(t){if(t.detail)return e.$message.error(t.detail),!1;e.dialogFormVisible=!1,e.$message({type:"success",message:"批量删除成功!",duration:500,onClose:function(){window.location.reload()}})})}}},u={render:function(){var e=this,t=e.$createElement,i=e._self._c||t;return i("div",{staticClass:"warp-box"},[i("curmbs"),e._v(" "),i("div",{staticClass:"container"},[i("handleBox",{attrs:{handleConfig:e.handleConfig},on:{delAll:e.delAll,search:e.search,newItem:e.newItem}}),e._v(" "),i("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),i("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t},opened:e.handleOpen}},[i("jsonForm",{ref:"formData",attrs:{handleType:e.handleType,formData:e.formData,formItems:e.formItems,formOptions:e.formOptions},on:{handleCancle:e.handleCancle,handleCofirm:e.handleCofirm}})],1)],1)],1)},staticRenderFns:[]};var g=i("C7Lr")(f,u,!1,function(e){i("VFCI")},"data-v-c5fc94f6",null);t.default=g.exports},VFCI:function(e,t){}});