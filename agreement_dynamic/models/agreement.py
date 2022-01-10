from odoo import fields, models, api


class Agreement(models.Model):
    _inherit = 'agreement'

    model_id = fields.Many2one('ir.model')
    res_id = fields.Integer(string='Record ID')
    resource_ref = fields.Reference(
        string='Record reference',
        selection='_selection_target_model',
        compute='_compute_resource_ref',
        inverse='_inverse_resource_ref'
    )

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    @api.depends('model_id', 'res_id')
    def _compute_resource_ref(self):
        for this in self:
            if this.model_id and this.res_id:
                this.resource_ref = '%s,%s' % (this.model_id.model, this.res_id)
            else:
                this.resource_ref = False

    def _inverse_resource_ref(self):
        for this in self:
            if this.resource_ref:
                this.res_id = this.resource_ref.id
                this.model_id = self.env['ir.model'].search([
                    ('model', '=', this.resource_ref._name)
                ], limit=1).id

    section_ids = fields.One2many('agreement.section', 'agreement_id')
