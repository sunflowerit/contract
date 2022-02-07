# Copyright 2022 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Report Dynamic",
    "version": "13.0.1.0.0",
    "category": "Agreement",
    "author": "Sunflower IT",
    "website": "https://sunflowerweb.nl",
    "license": "AGPL-3",
    "summary": "Dynamic Report Builder",
    "depends": ["base"],
    "data": [
        "security/res_groups.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "data/report_dynamic_alias.xml",
        "report/report_dynamic_report.xml",
        "views/report_dynamic_section.xml",
        "views/report_dynamic_alias.xml",
    ],
    "installable": True,
}
