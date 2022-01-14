import copy

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

from .header import Header

try:
    from jinja2.sandbox import SandboxedEnvironment

    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    # Let's keep these in case they are needed
    # in the future
    mako_template_env.globals.update(
        {
            "str": str,
            "len": len,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "filter": filter,
            "map": map,
            "round": round,
        }
    )
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    pass


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
    is_paragraph = fields.Boolean(
        default=True, string="Paragraph", help="To highlight lines"
    )

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
        for this in self:
            content = this._render_template(
                this.content,
                this.resource_ref_model_id.model,
                this.res_id,
                datas={"header": Header()},
            )
            this.dynamic_content = content

    def _get_proper_default_value(self):
        self.ensure_one()
        value = "''"
        if self.default_value:
            if self.field_id.ttype in ("integer", "float"):
                value = "{}"
            else:
                value = "'{}'"
            value = value.format(self.default_value)
        return value

    @api.model
    def _render_template(self, template_txt, model, res_ids, datas=False):
        """
        Render input provided by user, for report and preview
        It is an edited version of mail.template._render_template()
        """
        if isinstance(res_ids, int):
            res_ids = [res_ids]
        if datas and not isinstance(datas, dict):
            raise UserError(_("datas argument is not a proper dict"))
        results = dict.fromkeys(res_ids, u"")
        # try to load the template
        try:
            mako_env = mako_safe_template_env
            template = mako_env.from_string(tools.ustr(template_txt))
        except Exception:
            return False
        records = self.env[model].browse(
            it for it in res_ids if it
        )  # filter to avoid browsing [None]
        res_to_rec = dict.fromkeys(res_ids, None)
        for record in records:
            res_to_rec[record.id] = record
        # prepare template variables
        variables = {
            "ctx": self._context,  # context kw would clash with mako internals
            "page": "<p style='page-break-after:always;'/>",
        }
        if datas:
            variables.update(datas)
        for res_id, record in res_to_rec.items():
            variables["object"] = record
            try:
                render_result = template.render(variables)
            except Exception as e:
                raise UserError(
                    _("Failed to render template %r using values %r")
                    % (template, variables)
                    + "\n\n{}: {}".format(type(e).__name__, str(e))
                )
            if render_result == u"False":
                render_result = u""
            results[res_id] = render_result
        return results[res_ids[0]] or results
