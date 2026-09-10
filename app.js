const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const state = { employeePage: 1, importFile: null };

const views = {
  dashboard: ["Dashboard", "Visão geral dos aniversários e envios."],
  employees: ["Servidores", "Cadastre, consulte e edite os servidores."],
  import: ["Importar dados", "Valide sua planilha antes de gravar no banco."],
  birthdays: ["Aniversariantes", "Consulte os aniversários por mês."],
  history: ["Histórico de envios", "Acompanhe mensagens enviadas, simulações e falhas."],
};

function toast(message, isError=false){ const el=$("#toast"); el.textContent=message; el.className=`toast show${isError?' error':''}`; clearTimeout(window.__toast); window.__toast=setTimeout(()=>el.className='toast',3500); }
function esc(v){ return String(v ?? '').replace(/[&<>'"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
function formatDate(v){ if(!v) return '—'; const [y,m,d]=String(v).slice(0,10).split('-'); return `${d}/${m}/${y}`; }
function statusBadge(status){ const map={sent:['success','Enviado'],dry_run:['warning','Simulação'],failed:['danger','Falhou'],skipped:['neutral','Ignorado']}; const [c,t]=map[status]||['neutral',status]; return `<span class="badge ${c}">${t}</span>`; }

async function api(url, options={}){
  const response = await fetch(url, options);
  let data = null; try{ data = await response.json(); }catch{}
  if(!response.ok){ const detail=data?.detail; const message=typeof detail==='string'?detail:(detail?.message||JSON.stringify(detail)||`Erro HTTP ${response.status}`); throw new Error(message); }
  return data;
}

async function checkApi(){ try{ await api('/api/health'); $('#apiStatus').classList.add('ok'); }catch{ $('#apiStatus').classList.remove('ok'); } }

function showView(name){
  $$('.view').forEach(v=>v.classList.remove('active')); $$('.nav-item').forEach(v=>v.classList.remove('active'));
  $(`#view-${name}`).classList.add('active'); $(`.nav-item[data-view="${name}"]`).classList.add('active');
  $('#pageTitle').textContent=views[name][0]; $('#pageSubtitle').textContent=views[name][1];
  if(name==='dashboard') loadDashboard(); if(name==='employees') loadEmployees(); if(name==='birthdays') loadBirthdays(); if(name==='history') loadHistory();
}

async function loadDashboard(){
  try{
    const [d,b]=await Promise.all([api('/api/dashboard'),api('/api/birthdays/today')]);
    const metrics=[['Servidores',d.employees_total,`${d.active_total} ativos`],['Aniversários hoje',d.birthdays_today,'servidores ativos'],['Aniversários no mês',d.birthdays_month,'neste mês'],['Mensagens hoje',d.sent_today,d.failed_today?`${d.failed_today} falha(s)`:'sem falhas']];
    $('#dashboardCards').innerHTML=metrics.map(x=>`<div class="metric"><div class="label">${x[0]}</div><div class="value">${x[1]}</div><div class="hint">${x[2]}</div></div>`).join('');
    $('#todayBirthdays').innerHTML = b.items.length ? `<table><thead><tr><th>Nome</th><th>E-mail</th><th>Nascimento</th></tr></thead><tbody>${b.items.map(e=>`<tr><td><strong>${esc(e.full_name)}</strong></td><td>${esc(e.email)}</td><td>${formatDate(e.birth_date)}</td></tr>`).join('')}</tbody></table>` : '<div class="empty">Nenhum aniversariante hoje.</div>';
  }catch(e){ toast(e.message,true); }
}

async function loadEmployees(){
  const q=encodeURIComponent($('#employeeSearch').value.trim()); const active=$('#employeeActive').value;
  let url=`/api/employees?page=${state.employeePage}&page_size=20&q=${q}`; if(active!=='') url+=`&active=${active}`;
  try{
    const data=await api(url);
    $('#employeesTable').innerHTML=data.items.length?`<table><thead><tr><th>Nome</th><th>E-mail</th><th>Nascimento</th><th>Status</th><th></th></tr></thead><tbody>${data.items.map(e=>`<tr><td><strong>${esc(e.full_name)}</strong></td><td>${esc(e.email)}</td><td>${formatDate(e.birth_date)}</td><td>${e.active?'<span class="badge success">Ativo</span>':'<span class="badge neutral">Inativo</span>'}</td><td><div class="actions"><button class="small-button" onclick="editEmployee(${e.id})">Editar</button><button class="small-button" onclick="toggleEmployee(${e.id},${!e.active})">${e.active?'Desativar':'Ativar'}</button><button class="small-button" onclick="deleteEmployee(${e.id})">Excluir</button></div></td></tr>`).join('')}</tbody></table>`:'<div class="empty">Nenhum servidor encontrado.</div>';
    $('#employeePagination').innerHTML=`<button class="button secondary" ${data.page<=1?'disabled':''} onclick="employeePage(${data.page-1})">Anterior</button><span style="padding:10px">${data.page} de ${data.pages}</span><button class="button secondary" ${data.page>=data.pages?'disabled':''} onclick="employeePage(${data.page+1})">Próxima</button>`;
  }catch(e){ toast(e.message,true); }
}
window.employeePage=(p)=>{state.employeePage=p;loadEmployees();};

async function editEmployee(id){ try{const e=await api(`/api/employees/${id}`);$('#dialogTitle').textContent='Editar servidor';$('#employeeId').value=e.id;$('#fullName').value=e.full_name;$('#email').value=e.email;$('#birthDate').value=e.birth_date;$('#active').checked=e.active;$('#employeeDialog').showModal();}catch(e){toast(e.message,true);} }
window.editEmployee=editEmployee;
async function toggleEmployee(id,active){try{await api(`/api/employees/${id}/active?active=${active}`,{method:'PATCH'});toast('Status atualizado.');loadEmployees();}catch(e){toast(e.message,true);}} window.toggleEmployee=toggleEmployee;
async function deleteEmployee(id){if(!confirm('Deseja realmente excluir este servidor?'))return;try{await fetch(`/api/employees/${id}`,{method:'DELETE'}).then(r=>{if(!r.ok)throw new Error('Não foi possível excluir.');});toast('Servidor excluído.');loadEmployees();}catch(e){toast(e.message,true);}} window.deleteEmployee=deleteEmployee;

async function saveEmployee(ev){ev.preventDefault();const id=$('#employeeId').value;const body={full_name:$('#fullName').value.trim(),email:$('#email').value.trim(),birth_date:$('#birthDate').value,active:$('#active').checked};try{await api(id?`/api/employees/${id}`:'/api/employees',{method:id?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});$('#employeeDialog').close();toast(id?'Servidor atualizado.':'Servidor cadastrado.');loadEmployees();}catch(e){toast(e.message,true);}}

async function previewImport(){if(!state.importFile)return;const fd=new FormData();fd.append('file',state.importFile);$('#previewImportButton').disabled=true;try{const data=await api('/api/import/preview',{method:'POST',body:fd});const s=data.summary;const summary=[['Linhas',s.total_rows],['Válidas',s.valid_rows],['Inválidas',s.invalid_rows],['Já cadastradas',s.already_in_database],['Duplicadas',s.duplicate_in_file]];let html=`<div class="summary-grid">${summary.map(x=>`<div class="summary-item"><strong>${x[1]}</strong><span>${x[0]}</span></div>`).join('')}</div>`;if(data.errors.length){html+=`<div class="error-list"><strong>Corrija antes de importar:</strong>${data.errors.slice(0,20).map(x=>`<div>Linha ${x.line}: ${esc(x.error)}</div>`).join('')}</div>`;}if(data.rows.length){html+=`<div class="import-controls"><select id="importMode" class="input" style="max-width:270px"><option value="upsert">Atualizar e-mails existentes</option><option value="skip">Ignorar e-mails existentes</option></select><button id="commitImportButton" class="button primary" ${data.errors.length?'disabled':''}>Importar ${s.valid_rows} registro(s)</button></div><div style="overflow:auto;max-height:380px"><table><thead><tr><th>Nome</th><th>E-mail</th><th>Nascimento</th><th>Situação</th></tr></thead><tbody>${data.rows.map(r=>`<tr><td>${esc(r.full_name)}</td><td>${esc(r.email)}</td><td>${formatDate(r.birth_date)}</td><td>${r.exists_in_database?'<span class="badge warning">Já cadastrado</span>':'<span class="badge success">Novo</span>'}</td></tr>`).join('')}</tbody></table></div>`;}$('#importPreview').innerHTML=html;$('#commitImportButton')?.addEventListener('click',commitImport);}catch(e){toast(e.message,true);}finally{$('#previewImportButton').disabled=false;}}
async function commitImport(){const mode=$('#importMode').value;const fd=new FormData();fd.append('file',state.importFile);$('#commitImportButton').disabled=true;try{const d=await api(`/api/import/commit?mode=${mode}`,{method:'POST',body:fd});toast(`Importação concluída: ${d.created} novos, ${d.updated} atualizados, ${d.skipped} ignorados.`);$('#importPreview').innerHTML='';state.importFile=null;$('#importFile').value='';$('#importActions').classList.add('hidden');loadDashboard();}catch(e){toast(e.message,true);$('#commitImportButton').disabled=false;}}

async function sendToday(){if(!confirm('Deseja executar agora o envio dos aniversários de hoje?'))return;const b=$('#sendTodayButton');b.disabled=true;try{const d=await api('/api/birthdays/send',{method:'POST'});toast(`Processado: ${d.sent} enviado(s), ${d.skipped} ignorado(s), ${d.failed} falha(s).`);loadDashboard();}catch(e){toast(e.message,true);}finally{b.disabled=false;}}

function initMonths(){const names=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];$('#birthMonth').innerHTML=names.map((n,i)=>`<option value="${i+1}">${n}</option>`).join('');$('#birthMonth').value=new Date().getMonth()+1;}
async function loadBirthdays(){try{const m=$('#birthMonth').value;const d=await api(`/api/birthdays/month?month=${m}`);$('#birthdaysTable').innerHTML=d.items.length?`<table><thead><tr><th>Dia</th><th>Nome</th><th>E-mail</th></tr></thead><tbody>${d.items.map(e=>`<tr><td><strong>${String(e.birth_date).slice(8,10)}</strong></td><td>${esc(e.full_name)}</td><td>${esc(e.email)}</td></tr>`).join('')}</tbody></table>`:'<div class="empty">Nenhum aniversariante neste mês.</div>';}catch(e){toast(e.message,true);}}
async function loadHistory(){try{const status=$('#historyStatus').value;const dt=$('#historyDate').value;let url='/api/history?page_size=100';if(status)url+=`&status=${status}`;if(dt)url+=`&target_date=${dt}`;const d=await api(url);$('#historyTable').innerHTML=d.items.length?`<table><thead><tr><th>Data</th><th>Servidor</th><th>E-mail</th><th>Status</th><th>Detalhe</th></tr></thead><tbody>${d.items.map(h=>`<tr><td>${new Date(h.sent_at).toLocaleString('pt-BR')}</td><td>${esc(h.full_name)}</td><td>${esc(h.recipient_email)}</td><td>${statusBadge(h.status)}</td><td>${esc(h.error_message||h.provider_id||'—')}</td></tr>`).join('')}</tbody></table>`:'<div class="empty">Nenhum envio registrado.</div>';}catch(e){toast(e.message,true);}}

$$('.nav-item').forEach(b=>b.addEventListener('click',()=>showView(b.dataset.view)));
$('#refreshButton').addEventListener('click',()=>{const active=$('.nav-item.active').dataset.view;showView(active);});
$('#newEmployeeButton').addEventListener('click',()=>{$('#employeeForm').reset();$('#employeeId').value='';$('#active').checked=true;$('#dialogTitle').textContent='Novo servidor';$('#employeeDialog').showModal();});
$('#closeDialog').addEventListener('click',()=>$('#employeeDialog').close());$('#cancelDialog').addEventListener('click',()=>$('#employeeDialog').close());$('#employeeForm').addEventListener('submit',saveEmployee);
let searchTimer;$('#employeeSearch').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{state.employeePage=1;loadEmployees();},300);});$('#employeeActive').addEventListener('change',()=>{state.employeePage=1;loadEmployees();});
$('#sendTodayButton').addEventListener('click',sendToday);$('#birthMonth').addEventListener('change',loadBirthdays);$('#historyFilterButton').addEventListener('click',loadHistory);
const fileInput=$('#importFile'), drop=$('#dropZone');fileInput.addEventListener('change',()=>selectImportFile(fileInput.files[0]));['dragenter','dragover'].forEach(evt=>drop.addEventListener(evt,e=>{e.preventDefault();drop.classList.add('drag');}));['dragleave','drop'].forEach(evt=>drop.addEventListener(evt,e=>{e.preventDefault();drop.classList.remove('drag');}));drop.addEventListener('drop',e=>selectImportFile(e.dataTransfer.files[0]));function selectImportFile(file){if(!file)return;state.importFile=file;$('#fileName').innerHTML=`<strong>${esc(file.name)}</strong><br><small>${(file.size/1024).toFixed(1)} KB</small>`;$('#importActions').classList.remove('hidden');$('#importPreview').innerHTML='';}$('#previewImportButton').addEventListener('click',previewImport);

initMonths(); checkApi(); loadDashboard();
