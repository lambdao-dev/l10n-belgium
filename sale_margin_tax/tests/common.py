# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleMarginTaxCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "P"})

        vals_product = {"name": "P", "standard_price": 10.0}
        cls.product = cls.env["product.product"].create(vals_product)
        vals_product_2 = {"name": "P2", "standard_price": 5}
        cls.product_2 = cls.env["product.product"].create(vals_product_2)

        vals_tax = {"name": "Margin Tax", "amount": 21.0, "amount_type": "margin"}
        cls.tax_margin = cls.env["account.tax"].create(vals_tax)

        vals_tax_other = {"name": "Other Tax", "amount": 21.0, "amount_type": "percent"}
        cls.tax_other = cls.env["account.tax"].create(vals_tax_other)

        vals_tag_vat = {"name": "VAT", "applicability": "taxes"}
        cls.tag_vat = cls.env["account.account.tag"].create(vals_tag_vat)
        vals_tag_base = {"name": "Base", "applicability": "taxes"}
        cls.tag_base = cls.env["account.account.tag"].create(vals_tag_base)
        cls.tags = cls.tag_base + cls.tag_vat

        lines = cls.tax_margin.invoice_repartition_line_ids
        line_base = lines.filtered(lambda l: l.repartition_type == "base")
        line_margin = lines.filtered(lambda l: l.repartition_type == "tax")
        line_base.tag_ids = [(6, 0, cls.tag_base.ids)]
        line_margin.tag_ids = [(6, 0, cls.tag_vat.ids)]

        vals_sale = {
            "partner_id": cls.partner.id,
            "partner_invoice_id": cls.partner.id,
            "partner_shipping_id": cls.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product.name,
                        "product_id": cls.product.id,
                        "product_uom_qty": 4,
                        "product_uom": cls.product.uom_id.id,
                        "price_unit": 25.0,
                        "tax_id": [(6, 0, cls.tax_margin.ids)],
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product_2.name,
                        "product_id": cls.product_2.id,
                        "product_uom_qty": 1,
                        "product_uom": cls.product_2.uom_id.id,
                        "price_unit": 15.0,
                        "tax_id": [(6, 0, cls.tax_margin.ids)],
                    },
                ),
            ],
        }

        cls.sale = cls.env["sale.order"].create(vals_sale)

        langs = cls.env["res.lang"].with_context(active_test=False)
        cls.lang = langs.search([("code", "=", "fr_BE")])
        cls.lang.active = True
        # cls.env["ir.translation"].load_module_terms(["base"], [cls.lang.code])
