import{n as b,aa as T,as as W}from"./EchartsRenderer-c963c82b.js";import{f as d}from"./index-7f383368.js";function w(n){const t=n.replace(/\n{2,}/g,`
`);return W(t)}function E(n){const t=w(n),{children:e}=d(t),r=[[]];let i=0;function s(o,a="normal"){o.type==="text"?o.value.split(`
`).forEach((l,p)=>{p!==0&&(i++,r.push([])),l.split(" ").forEach(f=>{f&&r[i].push({content:f,type:a})})}):(o.type==="strong"||o.type==="emphasis")&&o.children.forEach(c=>{s(c,o.type)})}return e.forEach(o=>{o.type==="paragraph"&&o.children.forEach(a=>{s(a)})}),r}function j(n){const{children:t}=d(n);function e(r){return r.type==="text"?r.value.replace(/\n/g,"<br/>"):r.type==="strong"?`<strong>${r.children.map(e).join("")}</strong>`:r.type==="emphasis"?`<em>${r.children.map(e).join("")}</em>`:r.type==="paragraph"?`<p>${r.children.map(e).join("")}</p>`:`Unsupported markdown: ${r.type}`}return t.map(e).join("")}function L(n){return Intl.Segmenter?[...new Intl.Segmenter().segment(n)].map(t=>t.segment):[...n]}function S(n,t){const e=L(t.content);return g(n,[],e,t.type)}function g(n,t,e,r){if(e.length===0)return[{content:t.join(""),type:r},{content:"",type:r}];const[i,...s]=e,o=[...t,i];return n([{content:o.join(""),type:r}])?g(n,o,s,r):(t.length===0&&i&&(t.push(i),e.shift()),[{content:t.join(""),type:r},{content:e.join(""),type:r}])}function $(n,t){if(n.some(({content:e})=>e.includes(`
`)))throw new Error("splitLineToFitWidth does not support newlines in the line");return h(n,t)}function h(n,t,e=[],r=[]){if(n.length===0)return r.length>0&&e.push(r),e.length>0?e:[];let i="";n[0].content===" "&&(i=" ",n.shift());const s=n.shift()??{content:" ",type:"normal"},o=[...r];if(i!==""&&o.push({content:i,type:"normal"}),o.push(s),t(o))return h(n,t,e,o);if(r.length>0)e.push(r),n.unshift(s);else if(s.content){const[a,c]=S(t,s);e.push([a]),c.content&&n.unshift(c)}return h(n,t,e)}function v(n,t){t&&n.attr("style",t)}function k(n,t,e,r,i=!1){const s=n.append("foreignObject"),o=s.append("xhtml:div"),a=t.label,c=t.isNode?"nodeLabel":"edgeLabel";o.html(`
    <span class="${c} ${r}" `+(t.labelStyle?'style="'+t.labelStyle+'"':"")+">"+a+"</span>"),v(o,t.labelStyle),o.style("display","table-cell"),o.style("white-space","nowrap"),o.style("max-width",e+"px"),o.attr("xmlns","http://www.w3.org/1999/xhtml"),i&&o.attr("class","labelBkg");let l=o.node().getBoundingClientRect();return l.width===e&&(o.style("display","table"),o.style("white-space","break-spaces"),o.style("width",e+"px"),l=o.node().getBoundingClientRect()),s.style("width",l.width),s.style("height",l.height),s.node()}function m(n,t,e){return n.append("tspan").attr("class","text-outer-tspan").attr("x",0).attr("y",t*e-.1+"em").attr("dy",e+"em")}function M(n,t,e){const r=n.append("text"),i=m(r,1,t);x(i,e);const s=i.node().getComputedTextLength();return r.remove(),s}function N(n,t,e,r=!1){const s=t.append("g"),o=s.insert("rect").attr("class","background"),a=s.append("text").attr("y","-10.1");let c=0;for(const l of e){const p=u=>M(s,1.1,u)<=n,f=p(l)?[l]:$(l,p);for(const u of f){const y=m(a,c,1.1);x(y,u),c++}}if(r){const l=a.node().getBBox(),p=2;return o.attr("x",-p).attr("y",-p).attr("width",l.width+2*p).attr("height",l.height+2*p),s.node()}else return a.node()}function x(n,t){n.text(""),t.forEach((e,r)=>{const i=n.append("tspan").attr("font-style",e.type==="emphasis"?"italic":"normal").attr("class","text-inner-tspan").attr("font-weight",e.type==="strong"?"bold":"normal");r===0?i.text(e.content):i.text(" "+e.content)})}const H=(n,t="",{style:e="",isTitle:r=!1,classes:i="",useHtmlLabels:s=!0,isNode:o=!0,width:a=200,addSvgBackground:c=!1}={})=>{if(b.info("createText",t,e,r,i,s,o,c),s){const l=j(t),p={isNode:o,label:T(l).replace(/fa[blrs]?:fa-[\w-]+/g,u=>`<i class='${u.replace(":"," ")}'></i>`),labelStyle:e.replace("fill:","color:")};return k(n,p,a,i,c)}else{const l=E(t);return N(a,n,l,c)}};export{H as c};
