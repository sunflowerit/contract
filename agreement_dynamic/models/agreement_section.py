from odoo import fields, models, api


class AgreementSection(models.Model):
    _name = 'agreement.section'
    _description = 'Agreement Section'

    _order = "sequence"

    name = fields.Char("Name", required=True)
    title = fields.Char("Title")
    sequence = fields.Integer("Sequence", default=10)
    content = fields.Html("Content")
    dynamic_content = fields.Html(
        compute="_compute_dynamic_content",
        string="Dynamic Content",
    )
    agreement_id = fields.Many2one(
        "agreement.agreement", string="Agreement", ondelete="cascade")

    # Dynamic field editor
    field_id = fields.Many2one("ir.model.fields", string="Field")
    sub_object_id = fields.Many2one("ir.model", string="Sub-model")
    sub_model_object_field_id = fields.Many2one(
        "ir.model.fields", string="Sub-field")
    default_value = fields.Char("Default Value")
    copyvalue = fields.Char("Placeholder Expression")

    @api.onchange("field_id", "sub_model_object_field_id", "default_value")
    def onchange_copyvalue(self):
        self.sub_object_id = False
        self.copyvalue = False
        if self.field_id and not self.field_id.relation:
            self.copyvalue = "${{object.{} or {}}}".format(
                self.field_id.name, self.default_value or "''"
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
                self.default_value or "''",
            )

    # compute the dynamic content for jinja expression
    def _compute_dynamic_content(self):
        MailTemplates = self.env["mail.template"]
        for this in self:
            content = MailTemplates._render_template(
                this.content, "agreement.section", [this.id]
            )[this.id]
            this.dynamic_content = content


