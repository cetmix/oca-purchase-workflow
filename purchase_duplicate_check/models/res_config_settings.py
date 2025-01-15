from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    create_activity_repeating_orders = fields.Boolean(
        config_parameter="purchase_duplicate_check.create_activity_repeating_orders"
    )
    repeating_orders_activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type",
        config_parameter="purchase_duplicate_check.repeating_orders_activity_type_id",
        string="Activity",
    )

    @api.onchange("create_activity_repeating_orders")
    def _onchange_create_activity_repeating_orders(self):
        if not self.create_activity_repeating_orders:
            self.repeating_orders_activity_type_id = False
