#!/usr/bin/env python

"""Tests for `invoice_generator` package."""
from datetime import date
import os
from pathlib import Path
import pytest
from jinja2 import Template
from invoice_generator import invoice_generator, models


@pytest.fixture
def prestation():
    return models.Prestation(title="prestation",
                             unit_price=10.0,
                             quantity=2,
                             vat=10)


@pytest.fixture
def invoice(prestation):
    data = {
        "reference": "2021-001",
        "emited": date.today(),
        "issuer": models.Issuer(
            **{"company_name": "My Awesome Company with characters_to_escape!",
               "first_name": "Pierre",
               "last_name": "Qui roule",
               "siret": '0000000000',
               "intracom_vat": 'FRXXXXXXXXX',
               "address": models.Address(address="Champs de Mars",
                                         zip_code=75000,
                                         city='Paris'),
               "email": "contact@my-awesome-company.com",
               "rib": models.RIB(name="my awesome company",
                                 bic="FR XXX",
                                 iban="FR 00000 0000 0000")
               }
        ),
        "customer": models.Customer(
            first_name='Jean',
            last_name="Dupond",
            name="Dupond's company",
            email="jean.dupond@example.com",
            address=models.Address(address="17 Avenue des Champs-Elysées",
                                   zip_code=75000,
                                   city="Paris"),
            phone="+33 6 00 00 00 00"
        ),
        "prestations": [
            prestation
        ]
    }
    return models.Invoice(**data)


@pytest.fixture
def invoice_escaped(invoice):
    escaped_company_name = r"My Awesome Company with characters\_to\_escape!"
    invoice.issuer.company_name = escaped_company_name
    return invoice


@pytest.fixture
def project_path():
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def template_dir(project_path):
    return project_path / 'invoice_generator' / 'templates'


@pytest.fixture
def generator(invoice, template_dir, tmpdir):
    return invoice_generator.InvoiceGenerator(invoice,
                                              template_dir,
                                              'main.tex',
                                              tmpdir,
                                              'test')


def test_prestation_total_validator(prestation):
    assert prestation.total == 20


def test_prestation_total_vat_validator(prestation):
    assert prestation.total_vat == 2


def test_invoice_total_without_charge_validator(invoice):
    assert invoice.total_without_charge == 20


def test_invoice_total_vat_validator(invoice):
    assert invoice.total_vat == 2


def test_invoice_total_validator(invoice):
    assert invoice.total == 22


def test_invoice_pagination(invoice):
    invoice.prestations = invoice.prestations * 11
    assert len(invoice.paginated_prestations) == 2
    assert len(invoice.paginated_prestations[0]) == 10
    invoice.prestations = invoice.prestations * 2
    assert len(invoice.paginated_prestations) == 2
    assert len(invoice.paginated_prestations[0]) == 16
    invoice.prestations = invoice.prestations * 2
    assert len(invoice.paginated_prestations) == 3
    assert len(invoice.paginated_prestations[0]) == 16
    assert len(invoice.paginated_prestations[1]) == 20
    assert len(invoice.paginated_prestations[2]) == 8


def test_invoice_generator_template_dir_accessor(generator, template_dir):
    assert generator.template_dir == template_dir


def test_invoice_generator_bad_template_dir(generator, project_path):
    with pytest.raises(FileNotFoundError):
        generator.template_dir = project_path / "bad_directory"


def test_invoice_generator_template_dir_conversion(generator, template_dir):
    generator.template_dir = str(template_dir)
    assert generator.template_dir == template_dir


def test_invoice_generator_template_dir_setter(generator, template_dir):
    generator.template_dir = None
    assert generator.template_dir == template_dir


def test_invoice_generator_template_name_accessor(generator):
    assert generator.template_name == 'main.tex'


def test_invoice_generator_template_name_setter(generator):
    generator.template_name = None
    assert generator.template_name == "main.tex"


def test_invoice_generator_invoice_name_accessor(generator):
    assert generator.invoice_name == 'test'


def test_invoice_generator_invoice_name_setter(generator):
    generator.invoice_name = 'test.pdf'
    assert generator.invoice_name == 'test'


def test_invoice_generator_data_accessor(generator, invoice_escaped):
    assert generator.data == invoice_escaped


def test_invoice_generator_output_directory_setter(generator, template_dir):
    generator.output_directory = None
    assert generator.output_directory == template_dir


def test_invoice_generator_output_directory_setter_str(generator,
                                                       template_dir):
    generator.output_directory = str(template_dir)
    assert generator.output_directory == template_dir


def test_invoice_generator_file_to_compile_accessor(generator, tmpdir):
    assert generator._file_to_compile == tmpdir / 'test'


def test_invoice_generator_load_template(generator):
    generator._load_template()
    assert isinstance(generator._template, Template)


def test_invoice_generator_run(generator, tmpdir):
    generator.run()
    assert os.listdir(tmpdir) == ['test.pdf']


def test_invoice_generator_clean(generator, tmpdir):
    generator._load_template()
    generator._generate_tex()
    generator._compile_latex()._compile_latex()
    assert len(os.listdir(tmpdir)) == 6
    generator._clean()
    assert len(os.listdir(tmpdir)) == 1


def test_invoice_generator_compilation_failed(generator):
    with pytest.raises(ValueError):
        generator._compile_latex()
