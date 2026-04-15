# 📊 Performance Status Tracker

O **Performance Status Tracker** é um dashboard desenvolvido em Streamlit para monitoramento do status das avaliações de desempenho do Performance. Ele permite acompanhar a adesão, o progresso das avaliações e identificar pendências de forma rápida e centralizada.

---

## 🎯 Objetivo

O Performance Status Tracker foi criado para oferecer visibilidade em tempo real do status das avaliações, facilitando o acompanhamento da adesão e apoiando a tomada de decisão durante o ciclo avaliativo.

---


## 🌐 Acesso ao dashboard

🔗 Link do sistema: **[https://mindsightperformancetracker.streamlit.app]**

## 🚀 Funcionalidades

- 📌 KPIs de avaliações (total, concluídas e pendentes)
- 📋 Análise de status por grupo avaliativo
- 👥 Progresso por avaliador
- 🔎 Detalhamento individual das avaliações
- 🎛️ Filtros dinâmicos (gestor, área, cargo, senioridade)
- 📤 Exportação completa dos dados

---

## 📂 Arquivo de entrada

O dashboard utiliza o arquivo exportado da plataforma: 
```text
evaluations_by_pair.csv ou .xlsx
```

### Campos esperados

- Nome do Avaliador  
- Gestor do Avaliador  
- Área  
- Cargo  
- Senioridade  
- Nome do Avaliado  
- Grupo Avaliativo do Avaliado  
- Status  
- Chave do Avaliado  

---

## ▶️ Como executar localmente

```bash
pip install streamlit pandas plotly openpyxl xlsxwriter
streamlit run performance_status_tracker.py
```

---

## 🛠️ Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- XlsxWriter
