# -*- coding: utf-8 -*-
# Copyright 2018 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Agreement Dynamic",
    "version": "13.0.1.0.0",
    "category": "Agreement",
    "author": "Sunflower IT",
    "website": "https://sunflowerweb.nl",
    "license": "AGPL-3",
    "summary": "Dynamic Agreement Builder",
    "depends": [
        'agreement',
        'hr'
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/agreement.xml",
        "views/agreement_section.xml",
        "report/agreement_dynamic_report.xml",
    ],
    "installable": True,
}
