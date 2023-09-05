import{U as Q,r as k,a8 as W,D as X,m as $,b as Y,P as o,an as Z,o as i,e as y,c as e,x as a,a4 as K,u as t,R as c,H as r,a_ as ee,F as M,K as m,I as g,V as ae,ao as te,a$ as oe,a7 as se}from"./index-ef7aa48c.js";import{d as ne,a as le}from"./database-2818470e.js";import{_ as ce}from"./_plugin-vue_export-helper-c27b6911.js";import{C as re,D as de}from"./DatabaseOutlined-a293b150.js";const ie={key:0,class:"loading-container"},ue={key:1,class:"dataspace-container"},_e={__name:"DatabaseObjectDetail",setup(pe){const{t:s}=Q(),v=k(!0),j=W(),P=j.params.databaseId,S=j.params.objectId,w=k({}),n=k({}),V=async()=>{const l=await ne("get",{vid:P});l.status==200?w.value=l.data:K.error(l.msg)},B=async()=>{const l=await le("get",{oid:S});l.status==200?n.value=l.data:K.error(l.msg)};X(async()=>{v.value=!0,await Promise.all([V(),B()]),u.data=n.value.raw_data.segments,v.value=!1});const D=k("segments"),u=$({columns:[{title:"#",key:"index",dataIndex:"index",width:"50px"},{title:s("workspace.databaseObjectDetail.segment_text"),key:"text",dataIndex:"text",ellipsis:!0},{title:s("workspace.databaseObjectDetail.segment_word_counts"),key:"word_counts",dataIndex:"word_counts",width:"50px"}],data:[],loading:!1,current:1,pageSize:10,total:0,pagination:Y(()=>({total:u.total,current:u.current,pageSize:u.pageSize})),hoverRowOid:null,customRow:l=>({style:{cursor:"pointer"},onClick:async d=>{(d.target.classList.contains("ant-table-cell")||d.target.classList.contains("object-title"))&&(p.segmentIndex=l.index,p.text=l.text,p.keywords=l.keywords,p.open=!0)},onMouseenter:d=>{u.hoverRowOid=l.vid},onMouseleave:d=>{u.hoverRowOid=null}})}),p=$({open:!1,segmentIndex:0,text:"",keywords:[]});return(l,d)=>{const z=o("a-spin"),C=o("router-link"),h=o("a-breadcrumb-item"),F=o("a-breadcrumb"),I=o("a-col"),R=o("a-typography-link"),N=o("a-popconfirm"),U=o("a-table"),O=o("a-tab-pane"),A=o("a-divider"),b=o("a-descriptions-item"),H=o("a-descriptions"),L=o("a-tabs"),T=o("a-typography-paragraph"),E=o("a-modal"),q=o("a-card"),G=o("a-row"),J=Z("highlight");return v.value?(i(),y("div",ie,[e(z)])):(i(),y("div",ue,[e(G,{align:"center",gutter:[16,16]},{default:a(()=>[e(I,{xl:16,lg:18,md:20,sm:22,xs:24},{default:a(()=>[e(F,null,{default:a(()=>[e(h,null,{default:a(()=>[e(C,{to:"/data"},{default:a(()=>[e(t(re)),c(" "+r(t(s)("components.layout.basicHeader.data_space")),1)]),_:1})]),_:1}),e(h,null,{default:a(()=>[e(C,{to:`/data/${w.value.vid}`},{default:a(()=>[e(t(de)),c(" "+r(w.value.name),1)]),_:1},8,["to"])]),_:1}),e(h,null,{default:a(()=>[c(r(n.value.title),1)]),_:1})]),_:1})]),_:1}),e(I,{xl:16,lg:18,md:20,sm:22,xs:24},{default:a(()=>[e(q,{loading:v.value},{title:a(()=>[e(t(ee)),c(" "+r(n.value.title),1)]),default:a(()=>[e(L,{activeKey:D.value,"onUpdate:activeKey":d[0]||(d[0]=_=>D.value=_),"tab-position":"left"},{default:a(()=>[e(O,{key:"segments",tab:t(s)("workspace.databaseObjectDetail.segments")},{default:a(()=>[e(U,{customRow:u.customRow,columns:u.columns,"data-source":u.data,pagination:u.pagination},{bodyCell:a(({column:_,record:f})=>[_.key==="keywords"?(i(),y(M,{key:0},[c(r(f.keywords.join(", ")),1)],64)):_.key==="action"?(i(),y(M,{key:1},[f.status!="PR"?(i(),m(N,{key:0,placement:"leftTop",title:t(s)("workspace.databaseDetail.delete_confirm"),onConfirm:x=>l.deleteObject(f.oid)},{default:a(()=>[e(R,{type:"danger"},{default:a(()=>[c(r(t(s)("workspace.databaseDetail.delete")),1)]),_:1})]),_:2},1032,["title","onConfirm"])):g("",!0)],64)):g("",!0)]),_:1},8,["customRow","columns","data-source","pagination"])]),_:1},8,["tab"]),e(O,{key:"full-document",tab:t(s)("workspace.databaseObjectDetail.full_document")},{default:a(()=>{var _,f,x;return[((_=n.value.source_url)==null?void 0:_.length)>0?(i(),m(R,{key:0,href:n.value.source_url,target:"_blank"},{default:a(()=>[c(r(t(s)("workspace.databaseObjectDetail.source_url")),1)]),_:1},8,["href"])):g("",!0),((f=n.value.source_url)==null?void 0:f.length)>0?(i(),m(A,{key:1})):g("",!0),ae(e(t(te),{source:((x=n.value.raw_data)==null?void 0:x.text)||"",class:"custom-scrollbar markdown-body custom-hljs"},null,8,["source"]),[[J]])]}),_:1},8,["tab"]),e(O,{key:"params_info",tab:t(s)("workspace.databaseObjectDetail.params_info")},{default:a(()=>[e(H,{bordered:""},{default:a(()=>[e(b,{label:t(s)("workspace.databaseObjectCreate.split_method")},{default:a(()=>[c(r(t(s)(`workspace.databaseObjectCreate.split_method_${n.value.info.process_rules.split_method}`)),1)]),_:1},8,["label"]),n.value.info.process_rules.split_method!="delimeter"?(i(),m(b,{key:0,label:t(s)("workspace.databaseObjectCreate.chunk_length")},{default:a(()=>[c(r(n.value.info.process_rules.chunk_length),1)]),_:1},8,["label"])):g("",!0),n.value.info.process_rules.split_method=="delimeter"?(i(),m(b,{key:1,label:t(s)("workspace.databaseObjectCreate.delimiter")},{default:a(()=>[c(r(n.value.info.process_rules.delimiter),1)]),_:1},8,["label"])):g("",!0),e(b,{label:t(s)("workspace.databaseObjectCreate.remove_url_and_email")},{default:a(()=>[n.value.info.process_rules.remove_url_and_email?(i(),m(t(oe),{key:0})):(i(),m(t(se),{key:1}))]),_:1},8,["label"]),e(b,{label:t(s)("workspace.databaseObjectDetail.paragraph_counts")},{default:a(()=>[c(r(n.value.info.paragraph_counts),1)]),_:1},8,["label"]),e(b,{label:t(s)("workspace.databaseObjectDetail.word_counts")},{default:a(()=>[c(r(n.value.info.word_counts),1)]),_:1},8,["label"])]),_:1})]),_:1},8,["tab"])]),_:1},8,["activeKey"]),e(E,{open:p.open,"onUpdate:open":d[1]||(d[1]=_=>p.open=_),title:`# ${p.segmentIndex}`,onCancel:d[2]||(d[2]=_=>p.open=!1),footer:null},{default:a(()=>[e(T,{content:p.text},null,8,["content"])]),_:1},8,["open","title"])]),_:1},8,["loading"])]),_:1})]),_:1})]))}}},ve=ce(_e,[["__scopeId","data-v-89abffdc"]]);export{ve as default};
