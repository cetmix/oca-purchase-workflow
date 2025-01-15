# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from ast import literal_eval

from odoo import _, models


class ConfirmationWizard(models.TransientModel):
    _inherit = "confirmation.wizard"

    def confirm_pending_order(self, order):
        invalid_lines = order.order_line.filtered("pending_order_ids")
        if not invalid_lines:
            return
        message = invalid_lines._get_order_confirm_message()
        if not message:
            return
        return self.confirm_message(
            message,
            order,
            title=_("There are existing Requests for Quotations for:"),
            method="button_confirm",
        )

    def _create_po_activity(self, activity_type_id):
        res_ids = literal_eval(self.res_ids) if self.res_ids else []
        records = self.env[self.res_model].browse(res_ids)
        model_id = self.env["ir.model"]._get_id(records._name)
        activity_type = self.env["mail.activity.type"].browse(activity_type_id)
        for record in records:
            self.env["mail.activity"].create(
                {
                    "user_id": activity_type.default_user_id.id or self.env.user.id,
                    "activity_type_id": activity_type.id,
                    "res_id": record.id,
                    "res_model_id": model_id,
                    "note": self.message,
                }
            )

    def action_confirm(self):
        action_type_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "purchase_duplicate_check.repeating_orders_activity_type_id", False
            )
        )
        if self._context.get("skip_rfq_confirmation") and action_type_id:
            self._create_po_activity(int(action_type_id))
        return super().action_confirm()
