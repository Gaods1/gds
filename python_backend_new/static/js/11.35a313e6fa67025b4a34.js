webpackJsonp([11],{"8sR2":function(e,t){},"Brq+":function(e,t,a){"use strict";a.d(t,"d",function(){return i}),a.d(t,"e",function(){return n}),a.d(t,"a",function(){return o}),a.d(t,"c",function(){return s}),a.d(t,"b",function(){return p});var l=a("pxwZ"),r="/certified/team/",i=function(e){return Object(l.b)(r,e)},n=function(e){return Object(l.b)(r+e+"/")},o=function(e){return Object(l.d)(r,e)},s=function(e,t){return Object(l.c)(r+e+"/",t)},p=function(e){return Object(l.a)(r+e+"/")}},XXX0:function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var l=a("a3Yh"),r=a.n(l),i=a("aA9S"),n=a.n(i),o=a("D4TX"),s=a("GOyC"),p=a("R5Jg"),u=a("IkF9"),d=a("8V1Y"),c=a("9pcb"),g=a("Brq+"),h={data:function(){var e=this;return{state_arr:{1:"正常",2:"暂停"},pt_type_arr:{0:"企业",1:"个人",2:"组合"},dialogTitle:"",dialogFormVisible:!1,serial:"",currentEditLine:0,select_word:"",formData:{},handleType:"审核通过",check_type:"pass",formOptions:{labelWidth:"120px"},formItems:[{type:"select",prop:"account_code",label:"分配账号",$default:null,options:[],eleProps:{size:"medium",filterable:!0,placeholder:"请选择或搜索"},rules:[{required:!0,message:"请选择分配账号",trigger:"change"}]},{type:"input",prop:"pt_name",label:"技术团队名称",$default:null,eleProps:{size:"medium",placeholder:"请输入技术团队名称"},rules:[{required:!0,message:"请输入技术团队名称",trigger:"blur"}]},{type:"input",prop:"pt_abbreviation",label:"技术团队简称",$default:null,eleProps:{size:"medium",placeholder:"技术团队简称"},rules:[{required:!0,message:"请输入技术团队简称",trigger:"blur"}]},{type:"select",prop:"pt_type",label:"技术团队类型",$default:"",change:this.pyTypeChange,eleProps:{placeholder:"技术团队类型"},options:d.a.projectTeamOptions,rules:[{required:!0,message:"请选择技术团队类型",trigger:"change"}]},{type:"input",prop:"comp_name",label:"企业名称",$default:null,show:function(){return 0===e.formData.pt_type},eleProps:{size:"medium",placeholder:"请输入企业名称"},rules:[{required:!0,message:"请输入企业名称",trigger:"blur"}]},{type:"input",prop:"owner_license",label:"社会信用代码",$default:null,show:function(){return 0===e.formData.pt_type},eleProps:{size:"medium",placeholder:"统一社会信用代码"},rules:[{required:!0,message:"请输入统一社会信用代码",trigger:"blur"}]},{type:"select",prop:"major_code",label:"所属领域",$default:[],eleProps:{placeholder:"请选择所属领域",multiple:!0,collapseTags:!0},options:[],rules:[{type:"array",required:!0,message:"请选择所属领域",trigger:"change"}]},{type:"selectregion",prop:"pt_city",label:"归属城市",$default:"",eleProps:{placeholder:"请选择归属城市"},rules:[{type:"number",required:!0,message:"请选择归属城市",trigger:"change"}]},{type:"input",prop:"pt_homepage",label:"团队主页",$default:null,eleProps:{size:"medium",placeholder:"请输入团队主页"}},{type:"editor",prop:"pt_abstract",label:"团队简述",$default:null,defaultValue:"",eleProps:{size:"medium",placeholder:"请输入团队简述",type:"textarea"},rules:[{required:!0,message:"请输入团队简述",trigger:"blur"}]},{type:"editor",prop:"pt_describe",label:"团队描述",$default:null,defaultValue:"",eleProps:{size:"medium",placeholder:"请输入团队描述",type:"textarea"},rules:[{required:!0,message:"请输入团队描述",trigger:"blur"}]},{type:"input",prop:"pt_people_name",label:"管理人员姓名",$default:null,eleProps:{size:"medium",placeholder:"请输入管理人员姓名"},rules:[{required:!0,message:"请输入管理人员姓名",trigger:"blur"}]},{type:"input",prop:"pt_people_tel",label:"手机号码",$default:null,eleProps:{size:"medium",placeholder:"请输入管理人员手机号码",maxlength:11},rules:[{required:!0,message:"请输入管理人员手机号码",trigger:"blur",maxlength:11},{pattern:/^1[3|4|5|6|7|8|9]\d{9}$/,message:"请正确输入手机号",trigger:"blur"}]},{type:"select",prop:"pt_people_type",label:"证件类型",$default:"",eleProps:{placeholder:"请选择管理人员证件类型"},options:d.a.idTypeOptions,rules:[{type:"number",required:!0,message:"请选择管理人员证件类型",trigger:"change"}]},{type:"input",prop:"pt_people_id",label:"证件号码",$default:null,eleProps:{size:"medium",placeholder:"请输入管理人员证件号码"},rules:[{required:!0,message:"请输入管理人员证件号码",trigger:"change"}]},{type:"upload",prop:"idfront",label:"身份证正面",$default:null,defaultList:[],icon:a("qkrN"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idfront",rules:[]},{type:"upload",prop:"idback",label:"身份证背面",$default:null,defaultList:[],icon:a("Kyb6"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idback",rules:[]},{type:"upload",prop:"idphoto",label:"手持身份证",defaultList:[],$default:null,icon:a("knSM"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idphoto",rules:[]},{type:"upload",prop:"logo",label:"logo",defaultList:[],$default:null,icon:a("fB8s"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"logo",rules:[{type:"string",message:"请上传logo",trigger:"change"}]},{type:"upload",prop:"promotional",label:"宣传图片",defaultList:[],$default:null,icon:a("6pu8"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"logo",rules:[{type:"string",message:"请上传宣传图片",trigger:"change"}]}],pyTypeChange:function(t,a){0===t?(e.formItems[a+1].show=!0,e.formItems[a+2].show=!0):(e.formItems[a+1].show=!1,e.formItems[a+2].show=!1)},handleConfig:{searchTerms:[{value:"pt_name",label:"项目团队名称"},{value:"pt_code",label:"项目团队代码"}],newItemTxt:"新增技术团队",delBtn:""},total:0,list:[],columns:[{prop:"pt_name",label:"项目团队名称",align:"center",width:180},{prop:"pt_homepage",label:"团队主页url",align:"center",width:180},{prop:"pt_type",label:"团队种类",align:"center",width:150,render:function(t,a){return t("span",{},void 0===e.pt_type_arr[a.row.pt_type]?"不详":e.pt_type_arr[a.row.pt_type])}},{prop:"pt_people_name",label:"团队联系人",align:"center",width:100},{prop:"pt_people_tel",label:"团队联系电话",align:"center",width:100},{prop:"city",label:"地市",align:"center",width:100},{prop:"state",label:"状态",align:"center",width:"100",render:function(t,a){return t("el-tag",{props:{type:2===a.row.state?"danger":1===a.row.state?"success":"info"}},void 0===e.state_arr[a.row.state]?"不详":e.state_arr[a.row.state])}}],operates:{width:300,fixed:"right",list:[{label:"编辑",type:"warning",show:function(e,t){return!0},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,a){e.handleEdit(t,a)}},{label:"详情",type:"primary",show:function(e,t){return!0},icon:"el-icon-info",plain:!0,disabled:!1,method:function(t,a){e.handleDetail(t,a)}},{label:"删除",type:"danger",icon:"el-icon-delete",show:!0,plain:!1,disabled:!1,method:function(t,a){e.handleDel(t,a)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!1,index:!0}}},components:{jsonForm:u.a,curmbs:o.a,handleBox:s.a,opTable:p.a},methods:{handleCancle:function(){this.$refs.formData.resetForm(),this.dialogFormVisible=!1},handleClose:function(e){this.$refs.formData.resetForm(),e()},handleOpen:function(){this.$refs.formData.initSelect()},handleCofirm:function(e){var t=this;if(!this.$refs.formData.validateForm())return!1;"edit"==this.handleType?Object(g.c)(this.serial,e).then(function(e){e.detail?t.$message.error(e.detail):(t.list.splice(t.currentEditLine,1,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"编辑成功!"}),t.getList())}):Object(g.a)(e).then(function(e){e.detail?t.$message.error(e.detail):(t.list.splice(0,0,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"添加成功!"}),t.getList())})},newItem:function(){this.resetExtrForm(),this.getAllAccount(),this.dialogTitle="新增技术团队",this.currentEditLine=0,this.handleType="new",this.dialogFormVisible=!0},handleEdit:function(e,t){var a=this;this.resetExtrForm(),this.getAllAccount(),this.currentEditLine=t,this.dialogTitle="编辑企业信息",this.handleType="edit",this.serial=e.serial,this.dialogFormVisible=!0,this.formData=n()({},e),this.formItems.forEach(function(t,l){t.state&&e[t.prop]&&a.forMataFileList(t.state,e[t.prop],l),void 0!==t.defaultValue&&a.$nextTick(function(){a.$set(t,"defaultValue",e[t.prop])})})},forMataFileList:function(e,t,a){var l=this,i={};i.response=r()({},e,t),i.status="success",i.percentage="100",this.$nextTick(function(){l.formItems[a].defaultList.splice(0,1,i)})},resetExtrForm:function(){var e=this;this.formItems.forEach(function(t,a){e.$set(e.formData,t.prop,t.$default),t.state&&(t.defaultList=[]),void 0!==t.defaultValue&&(t.defaultValue=null)})},handleDel:function(e,t){var a=this;this.$confirm("此操作将永久删除该项, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){Object(g.b)(e.serial).then(function(e){e.detail?a.$message.error(e.detail):a.list.splice(t,1)}).then(function(){a.$message({type:"success",message:"删除成功!"})})}).catch(function(){a.$message({type:"info",message:"已取消删除"})})},getAllAccount:function(){var e=this;Object(c.g)({params:{admin:"false",page_size:"max"}}).then(function(t){for(var a in e.accountAll=[],t.data.results){var l=t.data.results,r={};r.value=l[a].account_code,r.label=l[a].user_name,e.accountAll.push(r)}for(var i in e.formItems)"account_code"==e.formItems[i].prop&&(e.formItems[i].options=e.accountAll)}),Object(c.h)().then(function(t){t.detail&&e.$message.error(t.detail),e.majorOptions=[];for(var a=0;a<t.data.results.length;a++){var l={};null!=t.data.results[a].mname&&(l.value=t.data.results[a].mcode,l.label=t.data.results[a].mname,l.key=a,e.majorOptions.push(l))}for(var r in e.formItems)"major_code"==e.formItems[r].prop&&(e.formItems[r].options=e.majorOptions)})},handleDetail:function(e,t){this.$router.push({name:"team_detail",query:{serial:e.serial}})},search:function(e,t){this.select_word=t,this.getList()},getList:function(){var e=this;this.options.loading=!0,Object(g.d)({params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}}).then(function(t){e.total=t.data.count,e.pagination.total=Number(t.data.count),e.list=t.data.results,e.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,console.log("handleSizeChange:"+this.pagination.pageSize),this.getList()},handleIndexChange:function(e){this.pagination=e,console.log("handleIndexChange:"+this.pagination.pageIndex),this.getList()},handleSelectionChange:function(e){console.log("val:",e)}}},m={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"warp-box"},[a("curmbs"),e._v(" "),a("div",{staticClass:"container"},[a("handleBox",{attrs:{handleConfig:e.handleConfig},on:{search:e.search,newItem:e.newItem}}),e._v(" "),a("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),a("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t},opened:e.handleOpen}},[a("jsonForm",{ref:"formData",attrs:{handleType:e.handleType,formData:e.formData,formItems:e.formItems,formOptions:e.formOptions},on:{handleCofirm:e.handleCofirm,handleCancle:e.handleCancle}})],1)],1)],1)},staticRenderFns:[]};var f=a("C7Lr")(h,m,!1,function(e){a("8sR2")},"data-v-07d7ae36",null);t.default=f.exports}});