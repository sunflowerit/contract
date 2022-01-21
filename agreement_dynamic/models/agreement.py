from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Agreement(models.Model):
    _inherit = "agreement"

    model_id = fields.Many2one("ir.model")
    res_id = fields.Integer(string="Record ID")
    resource_ref = fields.Reference(
        string="Record reference",
        selection="_selection_target_model",
        compute="_compute_resource_ref",
        inverse="_inverse_resource_ref",
    )
    template_id = fields.Many2one("ir.ui.view", domain="[('type', '=', 'qweb')]")
    documentation = fields.Text(default="Some documentation blah blah", readonly=True)
    alias_ids = fields.One2many("agreement.dynamic.alias", "agreement_id", copy=True)

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    @api.depends("model_id", "res_id")
    def _compute_resource_ref(self):
        for this in self:
            if this.model_id and this.res_id:
                this.resource_ref = "{},{}".format(this.model_id.model, this.res_id)
            else:
                this.resource_ref = False

    def _inverse_resource_ref(self):
        for this in self:
            if this.resource_ref:
                this.res_id = this.resource_ref.id
                this.model_id = (
                    self.env["ir.model"]
                    .search([("model", "=", this.resource_ref._name)], limit=1)
                    .id
                )

    def get_template_xml_id(self):
        self.ensure_one()
        if not self.template_id:
            # return a default
            return "web.external_layout"
        record = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", self.template_id.id)],
            limit=1,
        )
        return "{}.{}".format(record.module, record.name)

    section_ids = fields.One2many("agreement.section", "agreement_id", copy=True)
    section_count = fields.Integer(string="Sections", compute="_compute_section_count")

    @api.depends("section_ids")
    def _compute_section_count(self):
        for this in self:
            this.section_count = len(this.section_ids)

    def action_view_section(self):
        self.ensure_one()
        return {
            "name": _("Sections"),
            "type": "ir.actions.act_window",
            "res_model": "agreement.section",
            "view_mode": "tree,form",
            "target": "current",
            "context": dict(self._context),
            "domain": [("id", "in", self.section_ids.ids)],
        }

    def action_wizard_sign_agreement(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "wizard.sign.agreement",
            "view_mode": "form",
            "target": "new",
        }

    def action_validate_content(self):
        self.ensure_one()
        # If nothing happens, then
        # dynamic.content is renderable
        for this in self.section_ids:
            try:
                this.dynamic_content
            except Exception as e:
                raise UserError(
                    _(
                        "Failed to compute dynamic content"
                        " for section {}. Reason: {}"
                    ).format(this.name or this.id, str(e))
                )
