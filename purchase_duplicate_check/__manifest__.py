{
    "name": "Purchase Duplicate Check",
    "version": "16.0.1.0.0",
    "summary": "Prevents overordering in the Purchase app with a Confirmation Wizard, "
    "'Pending Orders' field, and activity tracking for repeated orders.",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Inventory/Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "live_test_url": "https://demo.cetmix.com",
    "depends": ["purchase_stock", "confirmation_wizard"],
    "external_dependencies": {},
    "data": [
        "views/purchase_order_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/confirmation_wizard_views.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
}
