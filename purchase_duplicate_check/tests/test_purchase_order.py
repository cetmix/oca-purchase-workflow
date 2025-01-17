from odoo.fields import Date
from odoo.tests import Form, TransactionCase


class TestPurchaseOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Vendor #1"})
        self.product_1 = self.env["product.product"].create(
            {"name": "Product 1", "detailed_type": "product"}
        )
        self.product_2 = self.env["product.product"].create(
            {"name": "Product 2", "detailed_type": "product"}
        )
        form = Form(self.env["purchase.order"])
        form.partner_id = self.partner
        with form.order_line.new() as line:
            line.product_id = self.product_1
            line.product_qty = 10.0
        self.order1 = form.save()

        self.activity_type_email = self.env.ref("mail.mail_activity_data_email")
        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_duplicate_check.allow_create_activity_repeating_orders", True
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_duplicate_check.repeating_orders_activity_type_id",
            self.activity_type_email.id,
        )

    def _get_and_create_purchase_order(self):
        form = Form(self.env["purchase.order"])
        form.partner_id = self.partner
        with form.order_line.new() as line:
            line.product_id = self.product_1
            line.product_qty = 5.0
        with form.order_line.new() as line:
            line.product_id = self.product_2
            line.product_qty = 5.0
        return form.save()

    def test_prepare_pending_orders_message(self):
        """Test flow where prepare message for purchase order"""
        message = self.order1._prepare_pending_orders_message(self.product_2.id)
        self.assertFalse(message, "Message must be empty")
        expected_message = f"RFQ: <a href='/web#id={self.order1.id}&model=purchase.order'>{self.order1.name}</a> date: {Date.today()} Qty: 10.0<br/>"  # noqa
        message = self.order1._prepare_pending_orders_message(self.product_1.id)
        self.assertEqual(message, expected_message, "Messages must be the same")

    def test_check_pending_order(self):
        """
        Test flow where check purchase order
        by exists pending orders for order lines
        """
        result = self.order1._check_pending_order()
        self.assertIsNone(result, "Result should be None")
        order2 = self._get_and_create_purchase_order()
        result = order2.with_context(skip_rfq_confirmation=True)._check_pending_order()
        self.assertIsNone(result, "Result should be None")
        result = order2._check_pending_order()
        self.assertIsInstance(result, dict, "Result should be dict")

    def test_button_confirm(self):
        """
        Test flow where check confirmation wizard at
        the confirmation purchase order
        """
        order1 = self.order1
        order2 = self._get_and_create_purchase_order()
        order3 = self._get_and_create_purchase_order()

        order3.with_context(skip_rfq_confirmation=True).button_confirm()

        self.assertEqual(order2.state, "draft", "Order should be draft")
        line1, line2 = order2.order_line
        self.assertEqual(
            line1.pending_order_ids,
            order1 | order3,
            "Pending orders should be the same",
        )
        self.assertEqual(
            line2.pending_order_ids, order3, "Pending orders should be the same"
        )

        result = order2.button_confirm()
        self.assertIsInstance(result, dict, "Result should be dict")

        wizard = self.env["confirmation.wizard"].browse(result["res_id"])
        self.assertEqual(wizard.res_ids, str(order2.ids), "Res IDS must be the same")
        self.assertEqual(wizard.res_model, order1._name, "Res Model must be the same")
        self.assertEqual(
            wizard.callback_method,
            "button_confirm",
            "Callback method must be 'nutton_confirm'",
        )

        result = wizard.with_context(skip_rfq_confirmation=True).action_confirm()
        self.assertTrue(result, "Result should be True")
        self.assertEqual(order2.state, "purchase", "Order state must be 'purchase'")
        activity = order2.activity_ids
        self.assertEqual(len(activity), 1)
        self.assertEqual(activity.user_id, self.env.user)
        self.assertEqual(activity.activity_type_id, self.activity_type_email)
