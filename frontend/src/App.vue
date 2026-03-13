<template>
  <div class="dashboard-elite">
    
    <header class="header-premium">
      <h1 class="logo-text">Números MKT</h1>
    </header>

    <main class="bento-container">
      
      <section class="card bento-item anim-1">
        <span class="tag-elite">VOLUMETRIA</span>
        <div class="volume-stack">
          <div class="stat-group">
            <label>LEADS</label>
            <strong class="num-med">{{ stats.leads }}</strong>
          </div>
          <div class="mini-divider"></div>
          <div class="stat-group">
            <label>VENDAS</label>
            <strong class="num-med gold-text">{{ stats.vendas }}</strong>
          </div>
        </div>
      </section>

      <section class="card bento-item anim-2">
        <span class="tag-elite">PERFORMANCE</span>
        <div class="conversao-inner">
          <h2 class="percent-med">{{ stats.conversao }}<small>%</small></h2>
          <p class="label-muted">Conversão Consolidada</p>
        </div>
      </section>

      <section class="card bento-item anim-3">
        <span class="tag-elite">PROJEÇÃO 15 DIAS</span>
        <div class="predicao-mini" v-if="predicao.leads_estimados">
          <div class="p-mini-row">
            <label>EST. LEADS</label>
            <strong class="num-mini">{{ predicao.leads_estimados }}</strong>
          </div>
          <div class="p-mini-row">
            <label>EST. VENDAS</label>
            <strong class="num-mini gold-glow">{{ predicao.vendas_estimadas }}</strong>
          </div>
        </div>
        <div v-else class="loading-state">Calculando tendência...</div>
      </section>

      <section class="card bento-grafico-full anim-4">
        <span class="tag-elite">VISUALIZER</span>
        <div class="chart-area-massive">
          <div class="donut-elite">
            <div class="donut-fill" :style="{ '--per': (stats.conversao * 3.6) + 'deg' }"></div>
            <div class="donut-hole"></div>
          </div>
        </div>
        <button @click="baixarPlanilha" class="btn-export-minimal">Exportar Relatório</button>
      </section>

      <transition name="portal">
        <div v-if="isAdmin" class="admin-overlay">
          <div class="admin-modal">
            <div class="modal-header">
              <span class="tag-elite">SYSTEM OVERRIDE</span>
              <button @click="isAdmin = false" class="btn-close-elite">FECHAR SISTEMA</button>
            </div>
            
            <div class="modal-body">
              <div class="input-container">
                <label>ENTRADA DE LEADS</label>
                <input type="number" v-model="tempForm.leads" class="input-glass-tech" placeholder="000" />
              </div>
              <div class="input-container">
                <label>ENTRADA DE VENDAS</label>
                <input type="number" v-model="tempForm.vendas" class="input-glass-tech" placeholder="000" />
              </div>
              <button @click="enviarParaBanco" class="btn-execute-elite">REGISTRAR NO MYSQL</button>
              
              <button @click="deletarUltimo" class="btn-delete-minimal">APAGAR ÚLTIMO REGISTRO</button>
            </div>
          </div>
        </div>
      </transition>

    </main>

    <footer class="footer-elite">
      <p class="legal">
        Developed for 
        <strong @dblclick="isAdmin = !isAdmin" class="secret-trigger">Joaquim Wronski</strong>
      </p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isAdmin = ref(false)
const stats = ref({ leads: 0, vendas: 0, conversao: 0 })
const predicao = ref({ leads_estimados: 0, vendas_estimadas: 0 })
const tempForm = ref({ leads: '', vendas: '' })

const carregarTudo = async () => {
  try {
    const resStats = await fetch('http://localhost:8000/buscar-metricas')
    stats.value = await resStats.json()
    const resPred = await fetch('http://localhost:8000/predicao-15-dias')
    const dataPred = await resPred.json()
    if (dataPred.status === "Sucesso") predicao.value = dataPred.proximo_ciclo
  } catch (e) { 
    console.error("Conexão offline") 
  }
}

const baixarPlanilha = () => window.open('http://localhost:8000/exportar-dados', '_blank')

const deletarUltimo = async () => {
  if (!confirm("⚠️ Apagar o último registro enviado?")) return;
  try {
    const res = await fetch('http://localhost:8000/deletar-ultimo', { method: 'DELETE' });
    if (res.ok) {
      alert("🗑️ Removido!");
      carregarTudo();
    }
  } catch (e) { alert("🚨 Erro ao deletar."); }
}

const enviarParaBanco = async () => {
  if (!tempForm.value.leads || !tempForm.value.vendas) return alert("Preencha os campos!");
  try {
    const conv = ((tempForm.value.vendas / tempForm.value.leads) * 100).toFixed(1);
    const res = await fetch('http://localhost:8000/salvar-metricas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data_registro: new Date().toISOString().split('T')[0],
        qtd_leads: tempForm.value.leads,
        qtd_vendas: tempForm.value.vendas,
        taxa_conversao: parseFloat(conv)
      })
    });
    if (res.ok) {
      alert("✅ REGISTRADO!");
      tempForm.value = { leads: '', vendas: '' };
      isAdmin.value = false;
      carregarTudo(); 
    }
  } catch (e) { alert("🚨 Erro de Conexão!"); }
}

onMounted(carregarTudo)
</script>

<style>
:root {
  --petroleo-deep: #010a0a;
  --petroleo-card: #021414;
  --ouro: #D4AF37;
  --ouro-glow: rgba(212, 175, 55, 0.3);
  --ouro-border: rgba(212, 175, 55, 0.4);
  --txt: #ffffff;
  --txt-dim: #4a5c5c;
}

body { margin: 0; background-color: var(--petroleo-deep); color: var(--txt); font-family: 'Inter', sans-serif; text-align: center; }
.dashboard-elite { max-width: 1300px; margin: 0 auto; padding: 80px 60px; box-sizing: border-box; }
.header-premium { margin-bottom: 60px; display: flex; justify-content: center; }
.logo-text { font-size: 2.2rem; font-weight: 900; letter-spacing: -2px; text-transform: uppercase; }
.bento-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }

.card { 
  background: var(--petroleo-card); border-radius: 32px; padding: 40px; 
  display: flex; flex-direction: column; align-items: center; justify-content: center; 
  border: 1px solid var(--ouro-border); box-shadow: 0 0 20px var(--ouro-glow); 
}

.bento-grafico-full { grid-column: span 3; min-height: 450px; }
.num-med { font-size: 3.5rem; font-weight: 900; line-height: 1; letter-spacing: -2px; }
.gold-text { color: var(--ouro); }
.mini-divider { height: 1px; background: rgba(255,255,255,0.05); width: 40%; margin: 20px auto; }
.percent-med { font-size: 5rem; font-weight: 900; color: var(--ouro); text-shadow: 0 0 20px var(--ouro-glow); }
.num-mini { font-size: 2rem; font-weight: 800; display: block; }
.gold-glow { color: var(--ouro); text-shadow: 0 0 10px var(--ouro-glow); }

.donut-elite { width: 220px; height: 220px; border-radius: 50%; position: relative; border: 1px solid var(--ouro-border); background: rgba(0,0,0,0.4); }
.donut-fill { 
  position: absolute; width: 100%; height: 100%; border-radius: 50%; 
  background: conic-gradient(var(--ouro) var(--per), transparent 0); /* VOLTOU AO OURO FIXO */
  transition: 1.5s ease; 
}
.donut-hole { position: absolute; width: 85%; height: 85%; background: var(--petroleo-card); border-radius: 50%; top: 7.5%; left: 7.5%; }

/* PAINEL */
.admin-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.94); backdrop-filter: blur(30px); z-index: 9999; display: flex; align-items: center; justify-content: center; }
.admin-modal { background: var(--petroleo-card); width: 90%; max-width: 500px; padding: 60px 40px; border-radius: 40px; border: 1px solid var(--ouro); box-shadow: 0 0 60px var(--ouro-glow); }
.input-glass-tech { background: transparent; border: none; border-bottom: 2px solid var(--txt-dim); color: #fff; font-size: 3.5rem; font-weight: 900; width: 100%; text-align: center; outline: none; margin: 20px 0; }
.btn-execute-elite { background: var(--ouro); color: #000; border: none; width: 100%; padding: 22px; border-radius: 16px; font-weight: 900; cursor: pointer; }

.btn-delete-minimal {
  background: transparent; border: 1px solid #ff4d4d; color: #ff4d4d;
  width: 100%; padding: 15px; border-radius: 15px; margin-top: 20px;
  font-weight: 900; font-size: 0.7rem; cursor: pointer; text-transform: uppercase;
}

.tag-elite { font-size: 0.6rem; font-weight: 900; color: var(--ouro); letter-spacing: 4px; margin-bottom: 25px; }
.btn-export-minimal { background: transparent; border: 1px solid var(--ouro-border); color: var(--ouro); padding: 8px 18px; border-radius: 10px; font-weight: 900; cursor: pointer; margin-top: 20px; }
.footer-elite { margin-top: 80px; opacity: 0.4; }
</style>