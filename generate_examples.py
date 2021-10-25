from invoice_generator import InvoiceGenerator
from invoice_generator.models import (Address, Customer, Issuer,
                                      Invoice, Prestation)
from datetime import datetime
from random import randint, random


def example(n_prestations, invoice_name):
    issuer = Issuer(
        first_name="first_name",
        last_name="last_name",
        company_name="company_name",
        siret="siret",
        intracom_vat="intracom_vat",
        email="email@example.com",
        phone="phone number",
        address=Address(address='address', zip_code=75000, city="Paris")
    )
    customer = Customer(
        first_name="first_name",
        last_name="last_name",
        # name="company_name",
        address=Address(address="address", zip_code=75000, city="Paris"),
        phone="phone number",
        email="email@example.com"
    )
    prestations = [
        Prestation(quantity=randint(1, 10),
                   unit_price=random() * 10,
                   title=f"prestation {i+1}"
                   ) for i in range(n_prestations)
    ]
    invoice = Invoice(issuer=issuer,
                      customer=customer,
                      prestations=prestations,
                      reference="reference",
                      emited=datetime.now())
    InvoiceGenerator(invoice,
                     invoice_name=invoice_name,
                     output_directory="./example").run()


if __name__ == "__main__":
    example(1, 'example_1')
    example(8, 'example_2')
    example(26, 'example_3')
