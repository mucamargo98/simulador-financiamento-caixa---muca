import streamlit as st

def calcular_parcela_SAC(valor_imovel, entrada, taxa_ano, prazo_meses):
    valor_financiado = valor_imovel - entrada
    amortizacao = valor_financiado / prazo_meses
    taxa_mensal = (1 + taxa_ano) ** (1/12) - 1
    juros_inicial = valor_financiado * taxa_mensal

    parcela_inicial = amortizacao + juros_inicial

    # Simula seguros e taxas extras aproximadas (opcional)
    seguro_mip = 0.0004 * valor_financiado  # exemplo: 0,04% do valor
    seguro_dfi = 40  # valor fixo médio
    taxa_admin = 25  # se quiser incluir

    parcela_total = parcela_inicial + seguro_mip + seguro_dfi + taxa_admin

    return round(parcela_total, 2)

def calcular_parcelas_completas(valor_financiado, taxa_efetiva_ano, prazo_meses):
    taxa_mensal = (1 + taxa_efetiva_ano) ** (1/12) - 1
    amortizacao = valor_financiado / prazo_meses
    parcelas = []
    saldo_devedor = valor_financiado
    for _ in range(prazo_meses):
        juros = saldo_devedor * taxa_mensal
        parcela = amortizacao + juros
        parcelas.append(round(parcela, 2))
        saldo_devedor -= amortizacao
    return parcelas

def simular_financiamento(renda, valor_imovel, taxa_efetiva_ano, prazo, comprom=0.3, pct_fin=0.7):
    max_parc = renda * comprom
    
    # Busca binária para encontrar o valor máximo financiável
    low, high = 0, valor_imovel * pct_fin
    
    for _ in range(50):
        mid = (low + high) / 2
        entrada_test = valor_imovel - mid
        
        # Usa a nova função que inclui seguros e taxas
        parcela_total = calcular_parcela_SAC(valor_imovel, entrada_test, taxa_efetiva_ano, prazo)
        
        if parcela_total > max_parc:
            high = mid
        else:
            low = mid
    
    valor_fin = low
    valor_entrada = valor_imovel - valor_fin
    
    # Calcula parcela inicial com seguros inclusos
    parcela_inicial_total = calcular_parcela_SAC(valor_imovel, valor_entrada, taxa_efetiva_ano, prazo)
    
    # Calcula parcela final (sem seguros para comparação)
    amort = valor_fin / prazo
    taxa_m = (1 + taxa_efetiva_ano)**(1/12) - 1
    juros_final = amort * taxa_m  # juros da última parcela são mínimos
    parcela_final_base = amort + juros_final
    
    # Gera todas as parcelas para histórico
    parcelas = calcular_parcelas_completas(valor_fin, taxa_efetiva_ano, prazo)
    
    return {
        "valor_financiado": round(valor_fin, 2),
        "valor_entrada": round(valor_entrada, 2),
        "parcela_inicial": round(parcela_inicial_total, 2),
        "parcela_final": round(parcela_final_base, 2),
        "parcelas": parcelas,
        "seguro_mip": round(0.0004 * valor_fin, 2),
        "seguro_dfi": 40,
        "taxa_admin": 25
    }

def renda_minima_para_financiar(valor_imovel, taxa_efetiva_ano, prazo_meses=420, percentual_financiamento=0.7, comprometimento=0.3):
    valor_financiado = valor_imovel * percentual_financiamento
    taxa_mensal = (1 + taxa_efetiva_ano) ** (1/12) - 1
    amortizacao = valor_financiado / prazo_meses
    parcela_inicial = amortizacao + (valor_financiado * taxa_mensal)
    renda_minima = parcela_inicial / comprometimento
    return renda_minima

def calcular_margem_erro(valor_real, valor_simulado):
    erro_absoluto = abs(valor_simulado - valor_real)
    margem_percentual = (erro_absoluto / valor_real) * 100
    return round(margem_percentual, 2)

st.set_page_config(
    page_title="Calculadora CEF - Muca", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para melhor responsividade
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Responsividade para mobile */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.8rem;
        }
        
        .stMetric {
            margin-bottom: 0.8rem;
        }
        
        .stColumns > div {
            padding: 0.3rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
            line-height: 1.3 !important;
        }
        
        h2, h3 {
            font-size: 1.2rem !important;
            margin: 1rem 0 0.5rem 0 !important;
        }
    }
    
    /* Containers com melhor contraste */
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        border-left: 4px solid #0066cc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        line-height: 1.5;
        border: 1px solid #bbdefb;
    }
    
    /* Melhor visibilidade de texto */
    .stMarkdown p {
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    /* Ajustes para inputs */
    .stNumberInput > label, .stSlider > label {
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    /* Melhor espaçamento para alertas */
    .stAlert {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 6px;
    }
    
    /* Expansor com melhor aparência */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏠 Calculadora de financiamento terreno construção CEF")
st.markdown("**Desenvolvido por Muca** - Sistema SAC com parâmetros CEF 2024")

st.markdown("---")

st.subheader("📋 Parâmetros do financiamento")

# Layout responsivo para inputs
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**Dados pessoais:**")
    renda = st.number_input(
        "Renda Mensal (R$)", 
        value=28295.00, 
        step=500.0, 
        format="%.2f",
        help="Sua renda mensal bruta"
    )
    
with col2:
    st.markdown("**Dados do imóvel:**")
    valor_imovel = st.number_input(
        "Valor do Imóvel (R$)", 
        value=1000000.00, 
        step=10000.0, 
        format="%.2f",
        help="Valor total do terreno + construção"
    )

# Segunda linha de inputs
col3, col4 = st.columns([1, 1])

with col3:
    prazo = st.slider(
        "Prazo do financiamento", 
        12, 420, 420, 
        step=12,
        format="%d meses",
        help="Prazo em meses (padrão CEF: 420 meses)"
    )
    st.caption(f"**{prazo} meses = {prazo//12} anos**")
    
with col4:
    taxa_efetiva_ano = st.number_input(
        "Taxa efetiva ao ano (%)", 
        value=12.00, 
        step=0.01, 
        format="%.2f",
        help="Taxa de juros efetiva anual"
    ) / 100

# Calcular resultado
resultado = simular_financiamento(renda, valor_imovel, taxa_efetiva_ano, prazo)
renda_necessaria = renda_minima_para_financiar(valor_imovel, taxa_efetiva_ano, prazo)

st.markdown("---")

st.subheader("📊 Resultado da simulação")

max_parcela_permitida = renda * 0.3

# Layout responsivo para métricas - 2x2 em telas pequenas
col_top1, col_top2 = st.columns(2)
col_bottom1, col_bottom2 = st.columns(2)

with col_top1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(
        "💰 Valor financiado", 
        f"R$ {resultado['valor_financiado']:,.2f}",
        help="Valor máximo que você pode financiar com sua renda"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
with col_top2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(
        "🏠 Entrada necessária", 
        f"R$ {resultado['valor_entrada']:,.2f}",
        help="Valor que precisa ser pago à vista"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
with col_bottom1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(
        "📈 Parcela inicial", 
        f"R$ {resultado['parcela_inicial']:,.2f}",
        help="Primeira parcela (maior no sistema SAC)"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
with col_bottom2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(
        "📉 Parcela final", 
        f"R$ {resultado['parcela_final']:,.2f}",
        help="Última parcela (menor no sistema SAC)"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Verificação de viabilidade com melhor formatação
comprometimento_atual = (resultado['parcela_inicial']/renda)*100

if resultado['parcela_inicial'] <= max_parcela_permitida:
    st.success(f"""
    ✅ **Financiamento viável!**  
    Parcela inicial dentro do limite de 30% da renda  
    **Comprometimento atual:** {comprometimento_atual:.1f}% (limite: 30%)
    """)
else:
    st.error(f"""
    ⚠️ **Parcela inicial excede 30% da renda**  
    **Comprometimento atual:** {comprometimento_atual:.1f}%  
    **Máximo permitido:** R$ {max_parcela_permitida:,.2f}
    """)

# Informações detalhadas organizadas
st.subheader("📋 Informações detalhadas")

# Primeiro bloco: Dados da simulação
st.markdown('<div class="info-box">', unsafe_allow_html=True)
st.markdown(f"""
**📊 Dados da simulação:**
- **Renda mensal:** R$ {renda:,.2f}
- **Valor do imóvel:** R$ {valor_imovel:,.2f}
- **Prazo:** {prazo} meses ({prazo//12} anos)
- **Taxa efetiva:** {taxa_efetiva_ano*100:.2f}% ao ano
""")
st.markdown('</div>', unsafe_allow_html=True)

# Segundo bloco: Composição do investimento
percentual_entrada = (resultado['valor_entrada'] / valor_imovel) * 100
percentual_financiado = (resultado['valor_financiado'] / valor_imovel) * 100
economia_ultima = resultado['parcela_inicial'] - resultado['parcela_final']

st.markdown('<div class="info-box">', unsafe_allow_html=True)
st.markdown(f"""
**💰 Composição do investimento:**
- **Entrada:** {percentual_entrada:.1f}% do imóvel (R$ {resultado['valor_entrada']:,.2f})
- **Financiamento:** {percentual_financiado:.1f}% do imóvel (R$ {resultado['valor_financiado']:,.2f})
- **Economia da 1ª para última parcela:** R$ {economia_ultima:,.2f}
""")
st.markdown('</div>', unsafe_allow_html=True)

# Terceiro bloco: Detalhamento de seguros e taxas
st.markdown('<div class="info-box">', unsafe_allow_html=True)
st.markdown(f"""
**🛡️ Seguros e taxas inclusos na parcela:**
- **Seguro MIP:** R$ {resultado['seguro_mip']:,.2f} (0,04% do valor financiado)
- **Seguro DFI:** R$ {resultado['seguro_dfi']:,.2f} (valor fixo mensal)
- **Taxa administrativa:** R$ {resultado['taxa_admin']:,.2f} (valor fixo mensal)
- **Total seguros/taxas:** R$ {resultado['seguro_mip'] + resultado['seguro_dfi'] + resultado['taxa_admin']:,.2f}
""")
st.markdown('</div>', unsafe_allow_html=True)

# Seção opcional para validação de precisão
st.subheader("🎯 Validação de precisão (opcional)")

with st.expander("Comparar com valores reais da CEF"):
    st.markdown("**Use esta seção para validar a precisão da simulação comparando com valores reais obtidos na CEF:**")
    
    col_val1, col_val2 = st.columns(2)
    
    with col_val1:
        valor_real_parcela = st.number_input(
            "Parcela real informada pela CEF (R$)", 
            value=0.0, 
            step=50.0, 
            format="%.2f",
            help="Digite o valor real da parcela informado pela CEF"
        )
        
    with col_val2:
        valor_real_renda = st.number_input(
            "Renda real aprovada pela CEF (R$)", 
            value=0.0, 
            step=500.0, 
            format="%.2f",
            help="Digite a renda que foi aprovada pela CEF"
        )
    
    if valor_real_parcela > 0:
        margem_parcela = calcular_margem_erro(valor_real_parcela, resultado['parcela_inicial'])
        
        if margem_parcela <= 5:
            st.success(f"✅ **Excelente precisão!** Margem de erro da parcela: {margem_parcela}%")
        elif margem_parcela <= 10:
            st.info(f"📊 **Boa precisão!** Margem de erro da parcela: {margem_parcela}%")
        else:
            st.warning(f"⚠️ **Diferença significativa.** Margem de erro da parcela: {margem_parcela}%")
        
        st.write(f"- **Parcela simulada:** R$ {resultado['parcela_inicial']:,.2f}")
        st.write(f"- **Parcela real CEF:** R$ {valor_real_parcela:,.2f}")
        st.write(f"- **Diferença:** R$ {abs(resultado['parcela_inicial'] - valor_real_parcela):,.2f}")
    
    if valor_real_renda > 0:
        margem_renda = calcular_margem_erro(valor_real_renda, renda)
        
        if margem_renda <= 3:
            st.success(f"✅ **Renda muito próxima!** Diferença: {margem_renda}%")
        elif margem_renda <= 8:
            st.info(f"📊 **Renda similar.** Diferença: {margem_renda}%")
        else:
            st.warning(f"⚠️ **Renda bem diferente.** Diferença: {margem_renda}%")
        
        st.write(f"- **Renda usada na simulação:** R$ {renda:,.2f}")
        st.write(f"- **Renda aprovada pela CEF:** R$ {valor_real_renda:,.2f}")
        st.write(f"- **Diferença:** R$ {abs(renda - valor_real_renda):,.2f}")

# Análise de viabilidade adicional
if renda < renda_necessaria:
    st.warning(f"""
    **💡 Análise para financiar 70% do imóvel (R$ {valor_imovel * 0.7:,.2f}):**  
    - **Renda mínima necessária:** R$ {renda_necessaria:,.2f}  
    - **Sua renda atual:** R$ {renda:,.2f}  
    - **Diferença:** R$ {renda_necessaria - renda:,.2f}
    """)
else:
    st.success("✅ **Sua renda é suficiente para financiar até 70% do imóvel!**")

# Rodapé responsivo
st.markdown("---")

# Disclaimer importante
st.warning("""
⚠️ **Importante:** Esta é uma simulação baseada nos parâmetros gerais da CEF.  
Os valores finais podem variar conforme análise de crédito, localização do imóvel e condições específicas.  
**Consulte sempre uma agência da CEF para informações oficiais.**
""")

# Informações do desenvolvedor
st.markdown("""
<div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-top: 1rem;">
    <small>
        <strong>📱 Desenvolvido por:</strong> Muca<br>
        <strong>🏦 Baseado em:</strong> Parâmetros CEF 2024<br>
        <strong>⚙️ Sistema:</strong> SAC (Sistema de Amortização Constante)
    </small>
</div>
""", unsafe_allow_html=True)