webpackJsonp([93],{LHoD:function(e,t,l){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var a=l("a3Yh"),r=l.n(a),i=l("aA9S"),n=l.n(i),s=l("D4TX"),o=l("GOyC"),p=l("R5Jg"),u=l("IkF9"),d=l("8V1Y"),c=l("9pcb"),g=l("1ILc"),m={data:function(){var e=this;return{state_arr:{1:"正常",2:"暂停"},accountAll:[],majorOptions:[],dialogTitle:"",dialogFormVisible:!1,serial:"",currentEditLine:0,select_word:"",formData:{},handleType:"审核通过",check_type:"pass",formOptions:{labelWidth:"160px"},formItems:[{type:"select",prop:"account_code",label:"分配账号",$default:null,options:[],eleProps:{size:"medium",filterable:!0,placeholder:"请选择或搜索"},rules:[{required:!0,message:"请选择分配账号",trigger:"change"}]},{type:"input",prop:"broker_name",label:"技术经理人名称",$default:null,eleProps:{size:"medium",placeholder:"请填写技术经理人名称"},rules:[{required:!0,message:"请输入技术经理人名称",trigger:"blur"},{min:2,max:64,message:"长度在2到64个字符",trigger:"blur"}]},{type:"input",prop:"broker_tel",label:"技术经理人电话",$default:null,eleProps:{size:"medium",placeholder:"请输入技术经理人电话",maxLength:14},rules:[{min:11,max:14,message:"固话要求11-14位(例:0312-0312345)",trigger:"blur"},{pattern:/^\d{3,4}-\d{7,8}$/,message:"请输入正确的固话",trigger:"blur"}]},{type:"input",prop:"broker_mobile",label:"技术经理人手机",$default:null,eleProps:{size:"medium",placeholder:"请输入技术经理人手机",maxLength:11},rules:[{required:!0,message:"请输入技术经理人手机",trigger:"blur"},{min:11,max:11,message:"手机号长度在11个字符",trigger:"blur"},{pattern:/^1[3-9]\d{9}$/,message:"请输入正确的手机号码",trigger:"blur"}]},{type:"input",prop:"broker_email",label:"技术经理人邮箱",$default:null,eleProps:{size:"medium",placeholder:"请填写技术经理人邮箱"},rules:[{min:3,max:64,message:"邮箱长度在3-64个字符",trigger:"blur"},{pattern:/^\w+@[a-zA-Z0-9]{2,10}(?:\.[a-z]{2,4}){1,3}$/,message:"请输入正确的邮箱",trigger:"blur"}]},{type:"select",prop:"broker_id_type",label:"技术经理人证件类型",eleProps:{placeholder:"请选择技术经理人证件类型"},options:[{label:"身份证",value:1},{label:"护照",value:2},{label:"驾照",value:3},{label:"军官证",value:4},{label:"其他",value:0}],rules:[{required:!0,message:"请选择技术经理人证件类型",trigger:"change"}]},{type:"input",prop:"broker_id",label:"技术经理人证件号码",$default:null,eleProps:{size:"medium",placeholder:"请填写技术经理人证件号码",maxLength:18},rules:[{required:!0,message:"请输入技术经理人证件号码",trigger:"blur"},{min:1,max:32,message:"技术经理人证件号码长度在1-32个字符",trigger:"blur"}]},{type:"select",prop:"major_code",label:"所属领域",$default:[],eleProps:{placeholder:"请选择所属领域",multiple:!0,collapseTags:!0},options:[],rules:[{type:"array",required:!0,message:"请选择所属领域",trigger:"change"}]},{type:"input",prop:"broker_address",label:"技术经理人通讯地址",$default:null,eleProps:{size:"medium",placeholder:"请填写技术经理人通讯地址"},rules:[{min:3,max:255,message:"技术经理人通讯地址长度在3-255个字符",trigger:"blur"}]},{type:"selectregion",prop:"broker_city",label:"归属城市",$default:"",eleProps:{placeholder:"请选择归属城市"},rules:[{type:"number",required:!0,message:"请选择归属城市",trigger:"change"}]},{type:"select",prop:"education",label:"学历信息",eleProps:{placeholder:"请选择学历信息"},options:[{label:"高中",value:"1"},{label:"大专",value:"2"},{label:"本科",value:"3"},{label:"硕士",value:"4"},{label:"博士",value:"5"}],rules:[{required:!0,message:"请选择学历信息",trigger:"change"}]},{type:"input",prop:"broker_graduate_school",label:"技术经理人毕业学校",$default:null,eleProps:{size:"medium",placeholder:"请填写技术经理人毕业学校"},rules:[{required:!0,message:"毕业学校必填",trigger:"change"},{min:3,max:255,message:"技术经理人毕业学校长度在3-255个字符",trigger:"blur"}]},{type:"input",prop:"broker_major",label:"技术经理人专业",$default:null,eleProps:{size:"medium",placeholder:"请填写技术经理人专业"},rules:[{required:!0,message:"技术经理人专业必填",trigger:"change"},{min:3,max:255,message:"技术经理人专业长度在1-64个字符",trigger:"blur"}]},{type:"editor",prop:"broker_abstract",label:"技术经理人简述",$default:null,defaultValue:"",eleProps:{size:"medium",placeholder:"请输入技术经理人简述",type:"textarea"},rules:[{required:!0,message:"请输入技术经理人简述",trigger:"blur"}]},{type:"input",prop:"broker_abbr",label:"技术经理人昵称",$default:null,eleProps:{size:"medium",placeholder:"请填写技术经理人昵称"},rules:[{min:2,max:32,message:"技术经理人昵称长度在2-32个字符",trigger:"blur"}]},{type:"input",prop:"broker_caption",label:"技术经理人头衔",$default:null,eleProps:{size:"medium",placeholder:"请填写技术经理人头衔"},rules:[{min:2,max:32,message:"技术经理人头衔长度在2-32个字符",trigger:"blur"}]},{type:"select",prop:"work_type",label:"工作方式",eleProps:{placeholder:"请选择工作方式"},options:[{label:"全职",value:1},{label:"兼职",value:2}],rules:[{required:!0,message:"请选择工作方式",trigger:"blur"}]},{type:"select",prop:"broker_level",label:"业务能力的内部的评级",eleProps:{placeholder:"请选择业务能力的内部的评级"},options:[{label:"1",value:1},{label:"2",value:2},{label:"3",value:3},{label:"4",value:4},{label:"5",value:5}],rules:[]},{type:"input-number",prop:"credit_value",label:"信用值",$default:null,eleProps:{size:"medium",placeholder:"请填写信用值",maxLength:3,min:0,max:100},rules:[{min:0,max:100,message:"信用值取值范围0-100，默认0",trigger:"blur",type:"number"}]},{type:"input-number",prop:"broker_integral",label:"积分",$default:null,eleProps:{size:"medium",placeholder:"请填写积分",maxLength:11,min:0,max:99999999999},rules:[{min:0,max:99999999999,message:"积分0-99999999999",trigger:"blur",type:"number"},{pattern:/^\d{1,10}$/,message:"请输入正确的积分",trigger:"blur"}]},{type:"upload",prop:"head",label:"头像",defaultList:[],$default:null,icon:l("qkrN"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"head",rules:[]},{type:"upload",prop:"idfront",label:"身份证正面",defaultList:[],$default:null,icon:l("qkrN"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idfront",rules:[]},{type:"upload",prop:"idback",label:"身份证背面",defaultList:[],$default:null,icon:l("Kyb6"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idback",rules:[]},{type:"upload",prop:"idphoto",label:"手持身份证",defaultList:[],$default:null,icon:l("knSM"),acceptType:".jpg,.jpeg,.png,.gif,.pdf,.JPG,.JPEG,.PNG,.GIF",state:"idphoto",rules:[]}],handleConfig:{searchTerms:[{value:"broker_name",label:"技术经理人名称"},{value:"broker_tel",label:"技术经理人电话"}],newItemTxt:"新增技术经理人",delBtn:""},total:0,list:[],columns:[{prop:"broker_name",label:"技术经理人姓名",align:"center",width:180},{prop:"broker_mobile",label:"技术经理人电话",align:"center",width:120},{prop:"education",label:"学历",align:"center",width:150,formatter:function(e,t,l){return d.a.education_arr[e.education]}},{prop:"broker_graduate_school",label:"毕业学校",align:"center",width:180},{prop:"broker_caption",label:"技术经理人头衔",align:"center",width:120},{prop:"state",label:"状态",align:"center",width:"120",render:function(t,l){return t("el-tag",{props:{type:2===l.row.state?"danger":1===l.row.state?"success":"info"}},void 0===e.state_arr[l.row.state]?"不详":e.state_arr[l.row.state])}},{prop:"credit_value",label:"信用值",align:"center",width:160}],operates:{width:300,fixed:"right",list:[{label:"详情",type:"primary",show:function(e,t){return!0},icon:"el-icon-info",plain:!0,disabled:!1,method:function(t,l){e.handleDetail(t,l)}},{label:"编辑",type:"warning",show:function(e,t){return!0},icon:"el-icon-edit",plain:!0,disabled:!1,method:function(t,l){e.handleEdit(t,l)}},{label:"删除",type:"danger",icon:"el-icon-delete",show:!0,plain:!1,disabled:!1,method:function(t,l){e.handleDel(t,l)}}]},pagination:{pageIndex:1,pageSize:10,show:!0,total:0},options:{stripe:!0,loading:!1,highlightCurrentRow:!0,mutiSelect:!1,index:!0}}},components:{curmbs:s.a,handleBox:o.a,opTable:p.a,jsonForm:u.a},methods:{handleCancle:function(){this.$refs.formData.resetForm(),this.dialogFormVisible=!1},handleClose:function(e){this.$refs.formData.resetForm(),e()},handleOpen:function(){this.$refs.formData.initSelect()},handleCofirm:function(e){var t=this;if(!this.$refs.formData.validateForm())return!1;"edit"==this.handleType?Object(g.c)(this.serial,e).then(function(e){e.detail&&t.$message.error(e.detail),t.list.splice(t.currentEditLine,1,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"编辑成功!"}),t.getList()}):Object(g.a)(e).then(function(e){e.detail&&t.$message.error(e.detail),t.list.splice(0,0,e),t.dialogFormVisible=!1,t.$message({type:"success",message:"添加成功!"}),t.getList()})},handleEdit:function(e,t){var l=this;this.resetExtrForm(),this.getAllAccount(),this.currentEditLine=t,this.dialogTitle="编辑技术经理人信息",this.handleType="edit",this.serial=e.serial,this.dialogFormVisible=!0,this.formData=n()({},e),this.formItems.forEach(function(t,a){t.state&&l.forMataFileList(t.state,e[t.prop],a),void 0!==t.defaultValue&&l.$nextTick(function(){l.$set(t,"defaultValue",e[t.prop])})})},forMataFileList:function(e,t,l){var a=this,i={};i.response=r()({},e,t),i.status="success",i.percentage="100",this.$nextTick(function(){a.formItems[l].defaultList.splice(0,1,i)})},resetExtrForm:function(){var e=this;this.formItems.forEach(function(t,l){e.$set(e.formData,t.prop,t.$default),t.state&&(t.defaultList=[]),void 0!==t.defaultValue&&e.$nextTick(function(){t.defaultValue=null})})},getAllAccount:function(){var e=this;Object(c.g)({params:{admin:"false",page_size:"max"}}).then(function(t){for(var l in t.detail&&e.$message.error(t.detail),e.accountAll=[],t.results){var a=t.results,r={};r.value=a[l].account_code,r.label=a[l].user_name,e.accountAll.push(r)}for(var i in e.formItems)"account_code"==e.formItems[i].prop&&(e.formItems[i].options=e.accountAll)}),Object(c.h)().then(function(t){t.detail&&e.$message.error(t.detail),e.majorOptions=[];for(var l=0;l<t.results.length;l++){var a={};null!=t.results[l].mname&&(a.value=t.results[l].mcode,a.label=t.results[l].mname,a.key=l,e.majorOptions.push(a))}for(var r in e.formItems)"major_code"==e.formItems[r].prop&&(e.formItems[r].options=e.majorOptions)})},handleDetail:function(e,t){this.$router.push({name:"broker_detail",query:{serial:e.serial}})},newItem:function(){this.resetExtrForm(),this.dialogTitle="新增技术经理人",this.getAllAccount(),this.currentEditLine=0,this.handleType="new",this.dialogFormVisible=!0},search:function(e,t){this.select_word=t,this.getList()},getList:function(){var e=this;this.options.loading=!0,Object(g.d)({params:{page:this.pagination.pageIndex,page_size:this.pagination.pageSize,search:this.select_word}}).then(function(t){t.detail&&e.$message.error(t.detail),e.total=t.count,e.pagination.total=Number(t.count),e.list=t.results,e.options.loading=!1})},handleSizeChange:function(e){this.pagination=e,console.log("handleSizeChange:"+this.pagination.pageSize),this.getList()},handleIndexChange:function(e){this.pagination=e,console.log("handleIndexChange:"+this.pagination.pageIndex),this.getList()},handleSelectionChange:function(e){},handleDel:function(e,t){var l=this;this.$confirm("此操作将永久删除, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then(function(){Object(g.b)(e.serial).then(function(e){e.detail&&l.$message.error(e.detail),l.list.splice(t,1)}).then(function(){l.$message({type:"success",message:"删除成功!"})})}).catch(function(){l.$message({type:"info",message:"已取消删除"})})}}},h={render:function(){var e=this,t=e.$createElement,l=e._self._c||t;return l("div",{staticClass:"warp-box"},[l("curmbs"),e._v(" "),l("div",{staticClass:"container"},[l("handleBox",{attrs:{handleConfig:e.handleConfig},on:{search:e.search,newItem:e.newItem}}),e._v(" "),l("opTable",{attrs:{list:e.list,total:e.total,options:e.options,pagination:e.pagination,columns:e.columns,operates:e.operates,getList:e.getList},on:{handleSizeChange:e.handleSizeChange,handleIndexChange:e.handleIndexChange,handleSelectionChange:e.handleSelectionChange}}),e._v(" "),l("el-dialog",{ref:"formDialog",attrs:{title:e.dialogTitle,visible:e.dialogFormVisible,"before-close":e.handleClose,modal:!1,"lock-scroll":!0},on:{"update:visible":function(t){e.dialogFormVisible=t},opened:e.handleOpen}},[l("jsonForm",{ref:"formData",attrs:{handleType:e.handleType,formData:e.formData,formItems:e.formItems,formOptions:e.formOptions},on:{handleCancle:e.handleCancle,handleCofirm:e.handleCofirm}})],1)],1)],1)},staticRenderFns:[]};var f=l("C7Lr")(m,h,!1,function(e){l("gLBF")},"data-v-06a87eb5",null);t.default=f.exports},gLBF:function(e,t){}});