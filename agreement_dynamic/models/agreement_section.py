import copy

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import safe_eval

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
            "page": "<p style='page-break-after:always;'/>",
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
    python_code = fields.Text(
        string="Condition", help="Condition for rendering section",
    )
    python_code_preview = fields.Char("Preview", compute="_compute_condition")
    show_in_report = fields.Boolean(compute="_compute_condition")

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

    @api.onchange("python_code")
    def _compute_condition(self):
        """Compute condition and preview"""
        for this in self:
            this.python_code_preview = this.show_in_report = False
            if not this.python_code:
                this.show_in_report = not this.python_code
                continue
            if not (this.resource_ref_model_id and this.res_id):
                continue
            record = self.env[this.resource_ref_model_id.model].browse(this.res_id)
            try:
                # Check if there are any syntax errors etc
                this.python_code_preview = safe_eval(
                    this.python_code.strip(), {"object": record}
                )
            except Exception as e:
                # and show debug info
                this.python_code_preview = str(e)
                continue
            is_valid = bool(this.python_code_preview)
            this.show_in_report = is_valid
            if not is_valid:
                # Preview is there, but condition is false
                this.python_code_preview = "False"

    def _get_proper_default_value(self):
        self.ensure_one()
        is_num = self.field_id.ttype in ("integer", "float")
        value = 0 if is_num else "''"
        if self.default_value:
            if is_num:
                value = "{}"
            else:
                value = "'{}'"
            value = value.format(self.default_value)
        return value

    # compute the dynamic content for jinja expression
    def _compute_dynamic_content(self):
        # a parent with two children
        h = Header(child=Header(child=Header()))
        for this in self:
            prerendered_content = this._prerender()
            content = this._render_template(
                prerendered_content,
                this.resource_ref_model_id.model,
                this.res_id,
                datas={"h": h},
            )
            this.dynamic_content = content

    def _prerender(self):
        """Substitute expressions using agreement.dynamic.alias records"""
        self.ensure_one()
        content = self.content
        for alias in self.env["agreement.dynamic.alias"].search(
            [("is_active", "=", True)]
        ):
            if alias.expression_from not in content:
                continue
            content = content.replace(alias.expression_from, alias.expression_to)
        return content

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
        mako_env = mako_safe_template_env
        template = mako_env.from_string(tools.ustr(template_txt))
        records = self.env[model].browse(
            it for it in res_ids if it
        )  # filter to avoid browsing [None]
        res_to_rec = dict.fromkeys(res_ids, None)
        for record in records:
            res_to_rec[record.id] = record
        # prepare template variables
        variables = {
            "ctx": self._context,  # context kw would clash with mako internals
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
