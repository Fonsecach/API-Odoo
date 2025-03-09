import re


def clean_vat(vat: str) -> str:
    cleaned_vat = ''.join(filter(str.isdigit, vat))

    len_vat = 14

    if len(cleaned_vat) != len_vat:
        raise ValueError(
            'CNPJ inválido. Deve conter exatamente 14 dígitos.'
        )

    return cleaned_vat


def validar_formato_nome(nome):
    pattern = r"^[A-Z\s]+\s\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"
    return re.match(pattern, nome) is not None
