# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Currency",
    "version": "16.0.1.0.0",
    "category": "Purchases",
    "license": "AGPL-3",
    "summary": "Select the default currency for purchases",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase", "sale", "stock"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
