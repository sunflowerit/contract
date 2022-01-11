from odoo import api, fields, models


class AgreementSection(models.Model):
    _name = "agreement.section"
    _description = "Agreement Section"

    _order = "sequence"

    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Sequence", default=10)
    content = fields.Html("Content")
    dynamic_content = fields.Html(
        compute="_compute_dynamic_content", string="Dynamic Content",
    )
    agreement_id = fields.Many2one("agreement", string="Agreement", ondelete="cascade")
    resource_ref = fields.Reference(related="agreement_id.resource_ref")
    res_id = fields.Integer(related="agreement_id.res_id")
    resource_ref_model_id = fields.Many2one("ir.model", related="agreement_id.model_id")

    # Dynamic field editor
    field_id = fields.Many2one("ir.model.fields", string="Field")
    sub_object_id = fields.Many2one("ir.model", string="Sub-model")
    sub_model_object_field_id = fields.Many2one("ir.model.fields", string="Sub-field")
    default_value = fields.Char("Default Value")
    copyvalue = fields.Char("Placeholder Expression")

    @api.onchange("field_id", "sub_model_object_field_id", "default_value")
    def onchange_copyvalue(self):
        self.sub_object_id = False
        self.copyvalue = False
        if self.field_id and not self.field_id.relation:
            self.copyvalue = "${{object.{} or {}}}".format(
                self.field_id.name, self._get_proper_default_value()
            )
            self.sub_model_object_field_id = False
        if self.field_id and self.field_id.relation:
            self.sub_object_id = self.env["ir.model"].search(
                [("model", "=", self.field_id.relation)]
            )[0]
        if self.sub_model_object_field_id:
            self.copyvalue = "${{object.{}.{} or {}}}".format(
                self.field_id.name,
                self.sub_model_object_field_id.name,
                self._get_proper_default_value(),
            )

    # compute the dynamic content for jinja expression
    def _compute_dynamic_content(self):
        MailTemplates = self.env["mail.template"]
        for this in self:
            content = MailTemplates._render_template(
                this.content, this.resource_ref_model_id.model, this.res_id,
            )
            this.dynamic_content = content

    def _get_proper_default_value(self):
        self.ensure_one()
        if not self.default_value:
            return "''"
        return "'{}'".format(self.default_value)
