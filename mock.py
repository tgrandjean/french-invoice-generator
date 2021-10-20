from invoice_generator.invoice_generator import InvoiceGenerator
from invoice_generator.models import (Address, Invoice, Issuer, RIB,
                                      Customer, Prestation)
from datetime import date
from random import randint, random, choice


def fake_prestations(number, variable_vat=False):
    return [
        Prestation(title=f"prestation {i + 1}",
                   unit_price=random() * randint(1, 10),
                   quantity=randint(1, 10),
                   vat=choice([10, 20]) if variable_vat else 0
                   ) for i in range(number)
    ]


data = {
    "reference": "2021-001",
    "emited": date.today(),
    "issuer": Issuer(
        **{"company_name": "My Awesome Company",
           "first_name": "Pierre",
           "last_name": "Qui roule",
           "siret": '0000000000',
           "intracom_vat": 'FRXXXXXXXXX',
           "address": Address(address="Champs de Mars",
                              zip_code=75000,
                              city='Paris'),
           "email": "contact@my-awesome-company.com",
           "rib": RIB(name="my awesome company",
                      bic="FR XXX",
                      iban="FR 00000 0000 0000")
           }
    ),
    "customer": Customer(
        first_name='Jean',
        last_name="Dupond",
        name="SARL Dupond et fils",
        email="jean.dupond@example.com",
        address=Address(address="17 Avenue des Champs-Elysées",
                        zip_code=75000,
                        city="Paris"),
        phone="+33 6 00 00 00 00"
    ),
    "prestations": fake_prestations(1, variable_vat=False)
}
data = Invoice(**data)

invoice_generator = InvoiceGenerator('./templates',
                                     'main.tex',
                                     data,
                                     output_directory='./example',
                                     invoice_name='test_2').run()
