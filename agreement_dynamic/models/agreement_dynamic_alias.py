from odoo import fields, models


class AgreementDynamicAlias(models.Model):
    _name = "agreement.dynamic.alias"
    _description = "Replace expressions before rendering"

    agreement_id = fields.Many2one("agreement", required=True, ondelete="cascade")
    expression_from = fields.Char(
        required=True, help="Look for this in agreement_id.section_ids.content"
    )
    expression_to = fields.Char(
        requires=True, help="Replace with this in agreement_id.section_ids.content"
    )
