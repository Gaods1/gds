webpackJsonp([15],{agTD:function(e,t,a){"use strict";a.d(t,"d",function(){return i}),a.d(t,"e",function(){return r}),a.d(t,"a",function(){return o}),a.d(t,"c",function(){return s}),a.d(t,"b",function(){return p});var l=a("pxwZ"),n="/certified/results_enterprise/",i=function(e){return Object(l.b)(n,e)},r=function(e){return Object(l.b)(n+e+"/")},o=function(e){return Object(l.d)(n,e)},s=function(e,t){return Object(l.c)(n+e+"/",t)},p=function(e){return Object(l.a)(n+e+"/")}},iurJ:function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var l=a("a3Yh"),n=a.n(l),i=a("aA9S"),r=a.n(i),o=a("D4TX"),s=a("GOyC"),p=a("R5Jg"),u=a("IkF9"),d=a("8V1Y"),c=a("9pcb"),g=a("agTD"),h={data:function(){var e=this;return{state_arr:{1:"正常",2:"暂停"},currentEditRow:{},accountAll:[],majorOptions:[],dialogTitle:"",dialogFormVisible:!1,serial:"",currentEditLine:0,select_word:"",formData:{},handleType:"审核通过",check_type:"pass",formOptions:{labelWidth:"120px"},formItems:[{type:"select",prop:"account_code",label:"分配账号",$default:null,options:[],eleProps:{size:"medium",filterable:!0,placeholder:"请选择或搜索"},rules:[{required:!0,message:"请选择分配账号",trigger:"change"}]},{type:"input",prop:"owner_name",label:"企业名称",$default:null,eleProps:{size:"medium",placeholder:"请输入企业名称"},rules:[{required:!0,message:"请输入企业名称",trigger:"blur"}]},{type:"input",prop:"owner_name_abbr",label:"企业简称",$default:null,eleProps:{size:"medium",placeholder:"请输入企业简称"},rules:[{required:!0,message:"请输入企业简称",trigger:"blur"}]},{type:"input",prop:"owner_license",label:"社会信用代码",$default:null,eleProps:{size:"medium",placeholder:"统一社会信用代码"},rules:[{required:!0,message:"请输入统一社会信用代码",trigger:"blur"}]},{type:"input",prop:"owner_tel",label:"企业电话",$default:null,eleProps:{size:"medium",placeholder:"请输入企业电话"},rules:[{required:!0,message:"请输入企业电话",trigger:"blur"},{pattern:/^(1[3|4|5|6|7|8|9]\d{9})|\d{3,4}-\d{7,8}$/,trigger:"blur",message:"示例：xxx-xxxxxxx或手机号码"}]},{type:"select",prop:"major_code",label:"所属领域",$default:[],eleProps:{placeholder:"请选择所属领域",multiple:!0,collapseTags:!0},options:[],rules:[{type:"array",required:!0,message:"请选择所属领域",trigger:"change"}]},{type:"selectregion",prop:"owner_city",label:"归属城市",show:!0,$default:null,eleProps:{placeholder:"请选择归属城市"},rules:[{required:!0,message:"请选择归属城市",trigger:"change"}]},{type:"input",prop:"homepage",label:"企业主页",$default:null,eleProps:{size:"medium",placeholder:"请输入企业主页"}},{type:"editor",prop:"owner_abstract",label:"企业简述",$default:null,defaultValue:"",eleProps:{size:"medium",placeholder:"请输入企业简述",type:"textarea"},rules:[{required:!0,message:"请输入企业简述",trigger:"blur"}]},{type:"upload",prop:"license",label:"企业营业执照",defaultList:[],$default:null,icon:a("fB8s"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"license",rules:[{type:"string",required:!0,message:"请上传企业营业执照",trigger:"change"}]},{type:"upload",prop:"logo",label:"企业logo",defaultList:[],$default:null,icon:a("NeCJ"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"logo"},{type:"upload",prop:"promotional",label:"企业宣传图片",defaultList:[],$default:null,icon:a("6pu8"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"promotional"},{prop:"owner_abstract_detail",label:"企业描述",$default:null,defaultValue:null,type:"editor",rules:[{required:!0,message:"请输入企业描述",trigger:"blur"}]},{type:"input",prop:"legal_person",label:"法人姓名",$default:null,eleProps:{size:"medium",placeholder:"请输入法人姓名"},rules:[{required:!0,message:"请输入管理人员姓名",trigger:"blur"}]},{type:"input",prop:"owner_mobile",label:"法人手机号码",$default:null,eleProps:{size:"medium",placeholder:"请输入法人手机号码",maxlength:11},rules:[{required:!0,message:"请输入法人手机号码",trigger:"blur",maxlength:11},{pattern:/^1[3|4|5|6|7|8|9]\d{9}$/,message:"请正确输入手机号",trigger:"blur"}]},{type:"select",prop:"owner_idtype",label:"证件类型",$default:null,eleProps:{placeholder:"请选择证件类型"},options:d.a.idTypeOptions,rules:[{type:"number",required:!0,message:"请选择证件类型",trigger:"change"}]},{type:"input",prop:"owner_id",label:"法人证件号码",$default:null,eleProps:{size:"medium",placeholder:"请输入证件号码"},rules:[{required:!0,message:"请输入证件号码",trigger:"change"}]},{type:"upload",prop:"idfront",label:"身份证正面",$default:null,defaultList:[],icon:a("qkrN"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idfront",rules:[]},{type:"upload",prop:"idback",label:"身份证背面",$default:null,defaultList:[],icon:a("Kyb6"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idback",rules:[]},{type:"upload",prop:"idphoto",label:"手持身份证",defaultList:[],$default:null,icon:a("knSM"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idphoto",rules:[]}],handleConfig:{searchTerms:[{value:"owner_name",label:"企业名称"},{value:"owner_mobile",label:"企业手机"}],newItemTxt:"新增持有企业",delBtn:""},total:0,list:[],columns:[{prop:"owner_name",label:"企业名称",align:"center",width:180},{prop:"owner_name_abbr",label:"企业简称",align:"center",width:180},{prop:"owner_mobile",label:"企业手机",align:"center",width:150},{prop:"homepage",label:"企业主页url",align:"center",width:180},{prop:"city",label:"归属城市",align:"center",width:150},{prop:"state",label:"状态",align:"center",width:"160",render:function(t,a){return t("el-tag",{props:{type:2===a.row.state?"danger":1===a.row.state?"success":"info"}},void 0===e.state_arr[a.row.state]?"不详":e.state_arr[a.row.state])}}],operates:{width:300,fixed:"right",list:[{label:"编辑",type:"warning",show:function(e,t){return!0},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,a){e.handleEdit(t,a)}},{label:"详情",type:"primary",show:function(e,t){return!0},icon:"el-icon-info",plain:!0,disabled:!1,method:function(t,a){e.handleDetail(t,a)}},{label:"删除",type:"danger",icon:"el-icon-delete",show:!0,plain:!1,disabled:!1,method:function(t,a){e.handleDel(t,a)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!1,index:!0}}},components:{curmbs:o.a,handleBox:s.a,opTable:p.a,jsonForm:u.a},methods:{handleCancle:function(){this.dialogFormVisible=!1},handleClose:function(){this.$refs.formData.resetForm()},handleOpen:function(){var e=this;if(this.$refs.formData.initSelect(),"new"==this.handleType)return!1;this.formData=this.currentEditRow,this.formItems.forEach(function(t,a){t.state&&e.currentEditRow[t.prop]&&e.forMataFileList(t.state,e.currentEditRow[t.prop],a),void 0!==t.defaultValue&&e.$set(t,"defaultValue",e.currentEditRow[t.prop])}),this.$nextTick(function(){e.$refs.formData.initSelect()})},handleCofirm:function(e){var t=this;if(!this.$refs.formData.validateForm())return!1;"edit"==this.handleType?Object(g.c)(this.serial,e).then(function(e){e.detail?t.$message.error(e.detail):(t.list.splice(t.currentEditLine,1,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"编辑成功!"}),t.getList())}):Object(g.a)(e).then(function(e){e.detail?t.$message.error(e.detail):(t.list.splice(0,0,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"添加成功!"}),t.getList())})},newItem:function(){this.resetExtrForm(),this.getAllAccount(),this.dialogTitle="新增持有企业",this.currentEditLine=0,this.handleType="new",this.dialogFormVisible=!0},handleEdit:function(e,t){this.resetExtrForm(),this.getAllAccount(),this.currentEditLine=t,this.dialogTitle="编辑企业信息",this.handleType="edit",this.serial=e.serial,this.dialogFormVisible=!0,this.currentEditRow=r()({},e)},forMataFileList:function(e,t,a){var l=this,i={};i.response=n()({},e,t),i.status="success",i.percentage="100",this.$nextTick(function(){l.formItems[a].defaultList.splice(0,1,i)})},resetExtrForm:function(){var e=this;this.formItems.forEach(function(t,a){e.$set(e.formData,t.prop,t.$default),t.state&&(t.defaultList=[]),void 0!==t.defaultValue&&e.$nextTick(function(){t.defaultValue=null})})},handleDel:function(e,t){var a=this;this.$confirm("此操作将永久删除该项, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){Object(g.b)(e.serial).then(function(e){e.detail?a.$message.error(e.detail):a.list.splice(t,1)}).then(function(){a.$message({type:"success",message:"删除成功!"})})}).catch(function(){a.$message({type:"info",message:"已取消删除"})})},getAllAccount:function(){var e=this;Object(c.g)({params:{admin:"false",page_size:"max"}}).then(function(t){for(var a in e.accountAll=[],t.data.results){var l=t.data.results,n={};n.value=l[a].account_code,n.label=l[a].user_name,e.accountAll.push(n)}for(var i in e.formItems)"account_code"==e.formItems[i].prop&&(e.formItems[i].options=e.accountAll)}),Object(c.h)().then(function(t){e.majorOptions=[];for(var a=0;a<t.data.results.length;a++){var l={};null!=t.data.results[a].mname&&(l.value=t.data.results[a].mcode,l.label=t.data.results[a].mname,l.key=a,e.majorOptions.push(l))}for(var n in e.formItems)"major_code"==e.formItems[n].prop&&(e.formItems[n].options=e.majorOptions)})},handleDetail:function(e,t){this.$router.push({name:"results_owner_enterprise_detail",query:{serial:e.serial}})},search:function(e,t){this.select_word=t,this.getList()},getList:function(){var e=this;this.options.loading=!0,Object(g.d)({params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}}).then(function(t){e.total=t.data.count,e.pagination.total=Number(t.data.count),e.list=t.data.results,e.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,console.log("handleSizeChange:"+this.pagination.pageSize),this.getList()},handleIndexChange:function(e){this.pagination=e,console.log("handleIndexChange:"+this.pagination.pageIndex),this.getList()},handleSelectionChange:function(e){console.log("val:",e)}}},f={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"warp-box"},[a("curmbs"),e._v(" "),a("div",{staticClass:"container"},[a("handleBox",{attrs:{handleConfig:e.handleConfig},on:{search:e.search,newItem:e.newItem}}),e._v(" "),a("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),a("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t},closed:e.handleClose,opened:e.handleOpen}},[a("jsonForm",{ref:"formData",attrs:{handleType:e.handleType,formData:e.formData,formItems:e.formItems,formOptions:e.formOptions},on:{handleCancle:e.handleCancle,handleCofirm:e.handleCofirm}})],1)],1)],1)},staticRenderFns:[]};var m=a("C7Lr")(h,f,!1,function(e){a("prZa")},"data-v-65a27ea6",null);t.default=m.exports},prZa:function(e,t){}});