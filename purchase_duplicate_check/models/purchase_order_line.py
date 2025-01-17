from odoo import _, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    pending_order_ids = fields.Many2many(
        "purchase.order",
        string="Pending Orders",
        compute="_compute_pending_order_ids",
    )

    def _compute_pending_order_ids(self):
        purchase_order_obj = self.env["purchase.order"]
        for rec in self:
            if rec.product_type != "product":
                rec.pending_order_ids = False
                continue
            rfq_orders = purchase_order_obj.search(
                [
                    ("order_line.product_id", "=", rec.product_id.id),
                    ("id", "!=", rec.order_id._origin.id),
                    "|",
                    ("state", "in", ["draft", "sent"]),
                    "&",
                    "&",
                    ("state", "not in", ["draft", "sent"]),
                    ("picking_ids.picking_type_id.code", "=", "incoming"),
                    ("picking_ids.state", "not in", ["done", "cancel"]),
                ]
            )
            rec.pending_order_ids = rfq_orders

    def _get_order_confirm_message(self):
        """Get order confirmation message for pending orders"""
        message = ""
        for line in self:
            pending_orders = line.pending_order_ids
            if not pending_orders:
                continue
            product_line_msg = pending_orders._prepare_pending_orders_message(
                line.product_id.id
            )
            message += f"""
            Product <b>{line.product_id.name}</b><br/>
            {product_line_msg}<br/>
            """
        return message

    def action_open_pending_orders(self):
        """Action open pending purchase orders"""
        self.ensure_one()
        return {
            "name": _("Pending Orders"),
            "views": [[False, "tree"], [False, "form"]],
            "res_model": "purchase.order",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.pending_order_ids.ids)],
            "context": {"create": False},
        }
