from odoo import fields, models, api


class AgreementTemplate(models.Model):
    _name = 'agreement.template'
    _description = 'Agreement Template'

    name = fields.Char("Template Name")

