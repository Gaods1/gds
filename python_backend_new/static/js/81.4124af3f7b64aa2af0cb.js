webpackJsonp([81],{TtQe:function(t,e){},w6zO:function(t,e,i){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var s=i("pxwZ"),a="/system/banner/",n={components:{uploadAttach:i("kiIx").a},data:function(){return{uploadedList:[],uploadSettings:{state:"banner",icon:"",limitNum:9,uploadTxt:"",uploadBtnTxt:"",listType:"pictures",acceptType:"image/*",defaultList:[]},imgList:[],selectedList:[],dialogTitle:"上传图片",dialogFormVisible:!1,serial:""}},mounted:function(){this.getList()},methods:{handleOpen:function(){this.dialogFormVisible=!0},delteItem:function(){var t=this;(function(t){return Object(s.a)(a+t+"/")})(this.$refs.transfer.leftChecked.join(",")).then(function(e){e.detail?t.$message.error(e.detail):(t.$message.success("删除成功"),t.getList())})},submit:function(t){var e=this;(function(t){return Object(s.d)(a,t)})({banner:this.uploadedList,state:t}).then(function(t){t.detail?e.$message.error(t.detail):(e.$message.success("上传成功"),e.dialogFormVisible=!1,e.uploadedList.splice(0),e.getList())})},renderImgList:function(t,e){return t("div",[t("img",{attrs:{width:"320",height:"180",src:e.banner},class:"image"}),t("div",{style:"padding: 4px"},[t("span",[e.file_name]),t("div",{class:"bottom clearfix"},[t("time",{class:"time"},[e.insert_time]),t("el-button",{attrs:{type:"text"},class:"button"},["操作按钮"])])])])},changeList:function(t,e,i){var n,l,o=this,r={state:"left"==e?0:1,serial:i};(n=i[0],l=r,Object(s.c)(a+n+"/",l)).then(function(t){t.detail?o.$message.error(t.detail):o.$message.success(t)})},getList:function(){var t,e=this;Object(s.b)(a,t).then(function(t){e.imgList=t.data.slice(0),e.selectedList=e.filterImg(1)})},filterImg:function(t){var e=[];return this.imgList.filter(function(i,s){i.state==t&&e.push(i.serial)}),e}}},l={render:function(){var t=this,e=t.$createElement,i=t._self._c||e;return i("div",{staticClass:"warp-box"},[i("el-transfer",{ref:"transfer",attrs:{data:t.imgList,"render-content":t.renderImgList,props:{key:"serial",label:"file_name"},titles:["图片库","展示中"],"button-texts":["移除展示","添加展示"],format:{noChecked:"${total}",hasChecked:"${checked}/${total}"}},on:{change:t.changeList},model:{value:t.selectedList,callback:function(e){t.selectedList=e},expression:"selectedList"}},[i("div",{staticClass:"transfer-footer",attrs:{slot:"left-footer"},slot:"left-footer"},[i("el-button",{attrs:{type:"primary"},on:{click:t.handleOpen}},[t._v("添加图片")]),t._v(" "),i("el-button",{attrs:{type:"danger"},on:{click:t.delteItem}},[t._v("删除")])],1)]),t._v(" "),i("el-dialog",{ref:"formDialog",attrs:{title:t.dialogTitle,visible:t.dialogFormVisible,modal:!1,"lock-scroll":!0},on:{"update:visible":function(e){t.dialogFormVisible=e}}},[i("uploadAttach",{ref:"uploadfile",attrs:{flag:t.uploadSettings.state,icon:t.uploadSettings.icon,limitNum:t.uploadSettings.limitNum,uploadTips:t.uploadSettings.uploadTxt||"",uploadBtnTxt:t.uploadSettings.uploadBtnTxt||"",listType:t.uploadSettings.listType,acceptType:t.uploadSettings.acceptType,defaultList:t.uploadSettings.defaultList},model:{value:t.uploadedList,callback:function(e){t.uploadedList=e},expression:"uploadedList"}}),t._v(" "),i("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[i("el-button",{on:{click:function(e){return t.submit(1)}}},[t._v("上传并展示")]),t._v(" "),i("el-button",{attrs:{type:"primary"},on:{click:function(e){return t.submit(0)}}},[t._v("上传到图库")])],1)],1)],1)},staticRenderFns:[]};var o=i("C7Lr")(n,l,!1,function(t){i("TtQe")},"data-v-468fc23d",null);e.default=o.exports}});