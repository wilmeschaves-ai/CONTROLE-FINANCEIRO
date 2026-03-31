def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def cor_valor(valor):
    if valor > 0:
        return "green"
    elif valor < 0:
        return "red"
    return "gray"
