# -*- coding: utf-8 -*-

import logging

from odoo import api, models, fields
from odoo.addons.sale_subscription.models.sale_order import SaleOrder, SUBSCRIPTION_PROGRESS_STATE
from odoo.osv import expression

_logger = logging.getLogger(__name__)


def _new_process_auto_invoice(self, invoice):
    """ Hook for extension, to support different invoice states """
    if self.plan_id.draft_invoice:
        self.with_context(mail_notrack=True).write({'payment_exception': False})
        self.env.cr.commit()
    else:
        invoice.action_post()
    return


def _new_recurring_invoice_domain(self, extra_domain=None):
    if not extra_domain:
        extra_domain = []
    current_date = fields.Date.today()
    search_domain = [('is_batch', '=', False),
                     ('is_invoice_cron', '=', False),
                     ('is_subscription', '=', True),
                     ('subscription_state', '=', '3_progress'),
                     ('payment_exception', '=', False),
                     ('pending_transaction', '=', False),
                     ('have_draft_invoice', '=', False),
                     '|', ('next_invoice_date', '<=', current_date), ('end_date', '<=', current_date)]
    if extra_domain:
        search_domain = expression.AND([search_domain, extra_domain])
    return search_domain


def _new_recurring_invoice_get_subscriptions(self, grouped=False, batch_size=30):
    """ Return a boolean and an iterable of recordsets.
    The boolean is true if batch_size is smaller than the number of remaining records
    If grouped, each recordset contains SO with the same grouping keys.
    """
    need_cron_trigger = False
    limit = False
    if self:
        domain = [('id', 'in', self.ids), ('subscription_state', 'in', SUBSCRIPTION_PROGRESS_STATE),
                  ('have_draft_invoice', '=', False)]
        batch_size = False
    else:
        domain = self._recurring_invoice_domain()
        limit = batch_size and batch_size + 1

    if grouped:
        all_subscriptions = self.read_group(
            domain,
            ['id:array_agg'],
            self._get_auto_invoice_grouping_keys(),
            limit=limit, lazy=False)
        all_subscriptions = [self.browse(res['id']) for res in all_subscriptions]
        need_cron_trigger = batch_size and len(all_subscriptions) > batch_size
        # We get a list of record sets when grouped is true. For each record set in all_subscriptions,
        # we call the '_get_subscriptions_to_invoice' method to process them.
        all_subscriptions = [subscription._get_subscriptions_to_invoice() for subscription in all_subscriptions]
    else:
        all_subscriptions = self.search(domain, limit=limit)
        need_cron_trigger = batch_size and len(all_subscriptions) > batch_size
        all_subscriptions = all_subscriptions._get_subscriptions_to_invoice()

    if batch_size:
        all_subscriptions = all_subscriptions[:batch_size]

    return all_subscriptions, need_cron_trigger


SaleOrder._process_auto_invoice = _new_process_auto_invoice
SaleOrder._recurring_invoice_domain = _new_recurring_invoice_domain
SaleOrder._recurring_invoice_get_subscriptions = _new_recurring_invoice_get_subscriptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    have_draft_invoice = fields.Boolean('Have a draft invoice', compute='_compute_have_draft_invoice',
                                        help='The subscription have currently a draft invoice', store=True)

    @api.depends('invoice_ids.state')
    def _compute_have_draft_invoice(self):
        for record in self:
            record.have_draft_invoice = False
            for invoice in record.invoice_ids:
                if invoice.state == 'draft':
                    record.have_draft_invoice = True
                    continue
