import streamlit as st
import pulp

st.title("Ottimizzazione dei Tagli delle Aste")
st.write("Inserisci i dati del problema per ottimizzare il numero di aste utilizzate.")

# Input della lunghezza dell'asta
rod_length = st.number_input("Lunghezza dell'asta (cm)", value=600, min_value=1)

# Numero di tipi di taglio
num_types = st.number_input("Numero di tipi di taglio", value=2, min_value=1, step=1)

# Creiamo due dizionari per le lunghezze dei tagli e le quantità richieste
cut_lengths = {}
required = {}
st.write("Inserisci i dettagli per ogni tipo di taglio:")
for i in range(int(num_types)):
    col1, col2 = st.columns(2)
    with col1:
        # Per impostare valori di default differenti
        default_cut = 20 if i == 0 else 30
        cut_lengths[i] = st.number_input(f"Lunghezza taglio {i+1} (cm)", value=default_cut, min_value=1, key=f"cut_len_{i}")
    with col2:
        default_qty = 5 if i == 0 else 2
        required[i] = st.number_input(f"Quantità richiesta per taglio {i+1}", value=default_qty, min_value=1, step=1, key=f"cut_qty_{i}")

# Bottone per avviare il calcolo
if st.button("Calcola Soluzione"):
    # Definiamo un numero massimo di aste (upper bound)
    max_rods = 10

    # Creazione del modello ILP
    model = pulp.LpProblem("Cutting_Stock", pulp.LpMinimize)

    # Variabili: x[i,j] = numero di tagli del tipo j sull'asta i
    x = pulp.LpVariable.dicts(
        "cut", ((i, j) for i in range(max_rods) for j in cut_lengths),
        lowBound=0, cat=pulp.LpInteger
    )
    # Variabili binarie: y[i] = 1 se l'asta i viene utilizzata, 0 altrimenti
    y = pulp.LpVariable.dicts(
        "rod_used", (i for i in range(max_rods)),
        cat=pulp.LpBinary
    )

    # Funzione obiettivo: minimizzare il numero di aste usate
    model += pulp.lpSum([y[i] for i in range(max_rods)]), "Minimize_rods_used"

    # Vincolo: ogni asta non può superare la lunghezza disponibile
    for i in range(max_rods):
        model += pulp.lpSum([cut_lengths[j] * x[(i, j)] for j in cut_lengths]) <= rod_length * y[i], f"Rod_length_constraint_{i}"

    # Vincolo: soddisfare la domanda per ogni tipo di taglio
    for j in cut_lengths:
        model += pulp.lpSum([x[(i, j)] for i in range(max_rods)]) == required[j], f"Demand_constraint_{j}"

    # Risolviamo il modello
    model.solve()

st.subheader("Risultati")
st.write("Stato della soluzione:", pulp.LpStatus[model.status])
st.write("Numero minimo di aste usate:", pulp.value(model.objective))

for i in range(max_rods):
    if pulp.value(y[i]) > 0:
        st.write(f"**Asta {i+1}**:")

        # Calcoliamo la lunghezza usata e stampiamo i dettagli di ogni taglio
        used_length = 0
        st.write("- Tagli effettuati:")
        for j in cut_lengths:
            num_cuts = int(pulp.value(x[(i, j)]))
            if num_cuts > 0:
                # Qui mostriamo la lunghezza del taglio e il numero di pezzi
                st.write(f"  - {cut_lengths[j]} cm: {num_cuts} pezzi")
                used_length += cut_lengths[j] * num_cuts

        # Calcoliamo lo scarto
        slack = rod_length - used_length
        st.write(f"- Lunghezza usata: {used_length} cm")
        st.write(f"- Scarto: {slack} cm")

