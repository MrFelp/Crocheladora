
import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Plataforma de Precificação", layout="wide")

def parse_number(v):
    if pd.isna(v) or v=="":
        return None
    # Try numeric
    try:
        return float(v)
    except:
        s = str(v).strip()
        # remove currency and spaces
        s = s.replace("R$", "").replace(" ", "")
        # If looks like Brazilian format like 1.234,56
        if s.count(",") == 1 and s.count(".") >= 1:
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", ".")
        try:
            return float(s)
        except:
            return None

def round_or_none(x, nd=2):
    try:
        return round(float(x), nd)
    except:
        return None

st.title("Plataforma de Precificação — Streamlit (versão leigo-friendly)")
st.markdown(
    """
    Carregue sua planilha (.xlsx/.csv). Em seguida mapeie as colunas (custo, quantidade, margem %, markup %, descrição).
    O app calculará preço de venda, lucro unitário e % automaticamente. Você pode editar valores e baixar o resultado.
    """
)

with st.expander("Instruções rápidas (leigo)"):
    st.markdown("""
- Passo 1: Clique em **Escolher arquivo** e selecione sua planilha Excel (.xlsx) ou CSV.
- Passo 2: Selecione nas caixas abaixo qual coluna corresponde a cada campo (o app tenta adivinhar automaticamente).
- Passo 3: Revise a tabela, edite células diretamente se precisar.
- Passo 4: Clique em **Baixar Excel** ou **Baixar CSV** para salvar o resultado.
    """)

uploaded = st.file_uploader("1) Selecione sua planilha (.xlsx / .csv)", type=["xlsx", "xls", "csv"])
sample_loaded = False

if uploaded is None:
    st.info("Você pode testar com um arquivo de amostra se preferir. (Não alterei sua planilha original.)")
    # Offer sample if exists in package
    try:
        sample_path = "sample_planilha_precificacao.xlsx"
        with open(sample_path, "rb") as f:
            pass
        if st.button("Carregar planilha de exemplo (sample)"):
            uploaded = open(sample_path, "rb")
            sample_loaded = True
    except FileNotFoundError:
        pass

df = None
if uploaded is not None:
    try:
        if getattr(uploaded, "name", "").lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded, engine="openpyxl")
        else:
            df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Falha ao ler o arquivo: {e}")

if df is not None:
    st.success(f"Planilha carregada — {df.shape[0]} linhas x {df.shape[1]} colunas")
    st.write("Amostra (primeiras linhas):")
    st.dataframe(df.head(10))

    cols = list(df.columns)
    st.markdown("### 2) Mapeamento de colunas (o app tenta adivinhar)")
    col1, col2, col3 = st.columns(3)
    with col1:
        cost_col = st.selectbox("Coluna de custo (custo/unit)", options=[""] + cols, index=cols.index(next((c for c in cols if "custo" in c.lower() or "valor" in c.lower() or "cost" in c.lower()), cols[0])) if cols else 0)
        qty_col = st.selectbox("Coluna de quantidade (opcional)", options=[""] + cols, index=cols.index(next((c for c in cols if any(x in c.lower() for x in ['qtd','quant','qty','quantidade'])), cols[0])) if cols else 0)
    with col2:
        margin_col = st.selectbox("Coluna de margem % (ex: 30)", options=[""] + cols, index=cols.index(next((c for c in cols if 'marg' in c.lower() or 'margin' in c.lower()), cols[0])) if cols else 0)
        markup_col = st.selectbox("Coluna de markup % (opcional)", options=[""] + cols, index=0)
    with col3:
        desc_col = st.selectbox("Coluna de descrição/produto", options=[""] + cols, index=cols.index(next((c for c in cols if any(x in c.lower() for x in ['desc','produto','nome','name'])), cols[0])) if cols else 0)

    # Build items dataframe normalized
    work = df.copy()
    # Ensure selected columns exist
    def get_col_val(r, col):
        if not col or col=="":
            return None
        return r.get(col, None)

    # Compute numeric columns
    costs = work[cost_col] if cost_col and cost_col in work.columns else None
    qtys = work[qty_col] if qty_col and qty_col in work.columns else None
    margins = work[margin_col] if margin_col and margin_col in work.columns else None
    markups = work[markup_col] if markup_col and markup_col in work.columns else None
    descs = work[desc_col] if desc_col and desc_col in work.columns else None

    # Create standardized table
    standard_rows = []
    for idx, row in work.iterrows():
        cost = parse_number(get_col_val(row, cost_col)) if cost_col else None
        qty = parse_number(get_col_val(row, qty_col)) if qty_col else 1
        margin = parse_number(get_col_val(row, margin_col)) if margin_col else None
        markup = parse_number(get_col_val(row, markup_col)) if markup_col else None
        desc = get_col_val(row, desc_col) if desc_col else str(row.name)
        # Default values
        if qty is None:
            qty = 1
        # Determine price preference: margin -> markup -> None
        price = None
        if margin is not None and not pd.isna(margin):
            try:
                price = cost / (1 - margin/100) if cost is not None else None
            except:
                price = None
        elif markup is not None and not pd.isna(markup):
            price = cost * (1 + markup/100) if cost is not None else None
        else:
            price = cost
        profit_unit = (price - cost) if (price is not None and cost is not None) else None
        profit_pct = (profit_unit / cost * 100) if (profit_unit is not None and cost not in (None,0)) else None
        standard_rows.append({
            "Descrição": desc,
            "Custo": round_or_none(cost,2),
            "Qtd": round_or_none(qty,2),
            "Margem_%": round_or_none(margin,2),
            "Markup_%": round_or_none(markup,2),
            "Preço_venda": round_or_none(price,2),
            "Lucro_un": round_or_none(profit_unit,2),
            "Lucro_%": round_or_none(profit_pct,2),
        })
    std_df = pd.DataFrame(standard_rows)
    st.markdown("### 3) Revise e edite (clique nas células para editar)")
    edited = st.experimental_data_editor(std_df, num_rows="dynamic")
    # Offer global settings: tax, freight
    st.markdown("### 4) Configurações globais (impostos / frete)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        tax_pct = st.number_input("Imposto (%) a aplicar sobre preço", value=0.0, step=0.1)
    with col_b:
        freight = st.number_input("Frete (valor absoluto por item)", value=0.0, step=0.01)
    with col_c:
        rounding = st.selectbox("Arredondamento", options=["Por item (unit)", "Por total"], index=0)
    # Recalculate price applying tax and freight
    final_rows = []
    for i, row in edited.iterrows():
        cost = parse_number(row.get("Custo"))
        price = parse_number(row.get("Preço_venda"))
        qty = parse_number(row.get("Qtd")) or 1
        if price is None and cost is not None:
            price = cost
        # apply tax and freight
        if price is not None:
            price_with_tax = price * (1 + tax_pct/100) + freight
        else:
            price_with_tax = None
        profit_unit = (price_with_tax - cost) if (price_with_tax is not None and cost is not None) else None
        profit_pct = (profit_unit / cost * 100) if (profit_unit is not None and cost not in (None,0)) else None
        final_rows.append({
            "Descrição": row.get("Descrição"),
            "Custo": round_or_none(cost,2),
            "Qtd": round_or_none(qty,2),
            "Preço_base": round_or_none(row.get("Preço_venda"),2),
            "Preço_final": round_or_none(price_with_tax,2),
            "Lucro_un": round_or_none(profit_unit,2),
            "Lucro_%": round_or_none(profit_pct,2),
        })
    final_df = pd.DataFrame(final_rows)
    st.markdown("### Resultado final")
    st.dataframe(final_df)
    # Totals
    total_cost = (final_df["Custo"] * final_df["Qtd"]).sum()
    total_revenue = (final_df["Preço_final"] * final_df["Qtd"]).sum()
    total_profit = total_revenue - total_cost
    st.markdown(f"**Totais:** Custo = {total_cost:.2f} | Receita = {total_revenue:.2f} | Lucro = {total_profit:.2f}")
    # Export buttons
    to_download = final_df.copy()
    # Excel
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        to_download.to_excel(writer, index=False, sheet_name="Precificacao")
    buf.seek(0)
    st.download_button("Baixar Excel (.xlsx)", data=buf, file_name=f"precificacao_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    # CSV
    csv_buf = to_download.to_csv(index=False).encode('utf-8')
    st.download_button("Baixar CSV", data=csv_buf, file_name=f"precificacao_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
    # Save profile: allow user to save to local storage via download of JSON
    json_buf = to_download.to_json(orient="records").encode('utf-8')
    st.download_button("Baixar JSON (backup)", data=json_buf, file_name="precificacao_backup.json", mime="application/json")

else:
    st.info("Aguardando upload da planilha. Você pode usar uma planilha do Excel (.xlsx) ou arquivo CSV.")
