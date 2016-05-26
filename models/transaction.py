from openerp import models, fields, api
from .. import misc

class EbTransaction(models.Model):
    _name = 'eb.transaction'
    _description = 'Transaction'

    name = fields.Char()
    eb_2_service_identifier = fields.Char(size=19)
    eb_3_transaction_type = fields.Selection(misc.TRANSACTION_TYPE)
    platform = fields.Selection(misc.PLATFORM, default='01', required=True)
    eb_4_total_value = fields.Float(digits=(18, 2))
    eb_7_date_time = fields.Char()
    eb_11_location_code = fields.Char(size=6)
    eb_11_sequential = fields.Char()
    eb_12_local_transaction_time = fields.Char(size=6)
    eb_13_local_transaction_date = fields.Char(size=8)
    eb_15_compensation_date = fields.Char(size=8)
    eb_19_consult_criterion = fields.Selection(misc.CONSULT_CRITERION)
    eb_23_service_type = fields.Selection(misc.SERVICE_TYPE)
    eb_28_doc = fields.Char(size=20)
    eb_32_setting_id = fields.Many2one('eb.setting')
    eb_42_pay_id = fields.Char(size=12)
    eb_43_back_reason = fields.Selection(misc.BACK_REASON)
    eb_45_name_lastname = fields.Char(size=35)
    eb_48_address = fields.Char(size=200)
    eb_49_currency_type = fields.Char(size=3)
    eb_70_administrative_transaction_code = fields.Char()
    flag_eb_2 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_4 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_7 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_11 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_12 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_13 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_15 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_19 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_23 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_28 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_32 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_42 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_43 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_45 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_48 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_49 = fields.Boolean(compute='_set_flag', default=False)
    flag_eb_70 = fields.Boolean(compute='_set_flag', default=False)
    mit = fields.Char()
    telephony = fields.Char()
    response = fields.Char()


    _order = 'name'

    _sql_constraints = [
        ('name_uk', 'unique(name)', 'Transaction must be unique'),
    ]
    @api.one
    @api.depends('eb_3_transaction_type','platform')
    def _set_flag(self):
        if self.eb_3_transaction_type == '000003' and self.platform == '01':
            self.flag_eb_2 = True
            self.flag_eb_4 = False
            self.flag_eb_11 = False
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = True
            self.flag_eb_23 = True
            self.flag_eb_28 = False
            self.flag_eb_32 = True
            self.flag_eb_42 = False
            self.flag_eb_43 = False
            self.flag_eb_45 = False
            self.flag_eb_48 = False
            self.flag_eb_49 = False
        if self.eb_3_transaction_type == '000003' and self.platform == '02':
            self.flag_eb_2 = True
            self.flag_eb_4 = False
            self.flag_eb_11 = False
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = True
            self.flag_eb_23 = True
            self.flag_eb_28 = False
            self.flag_eb_32 = True
            self.flag_eb_42 = False
            self.flag_eb_43 = False
            self.flag_eb_45 = False
            self.flag_eb_48 = False
            self.flag_eb_49 = False
        if self.eb_3_transaction_type == '000003' and self.platform == '03':
            self.flag_eb_2 = False
            self.flag_eb_4 = False
            self.flag_eb_11 = False
            self.flag_eb_12 = False
            self.flag_eb_13 = False
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = False
            self.flag_eb_28 = False
            self.flag_eb_32 = False
            self.flag_eb_42 = False
            self.flag_eb_43 = False
            self.flag_eb_45 = False
            self.flag_eb_48 = False
            self.flag_eb_49 = False
        if self.eb_3_transaction_type == '000003' and self.platform == '04':
            self.flag_eb_2 = False
            self.flag_eb_4 = False
            self.flag_eb_11 = False
            self.flag_eb_12 = False
            self.flag_eb_13 = False
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = False
            self.flag_eb_28 = False
            self.flag_eb_32 = False
            self.flag_eb_42 = False
            self.flag_eb_43 = False
            self.flag_eb_45 = False
            self.flag_eb_48 = False
            self.flag_eb_49 = False
        if self.eb_3_transaction_type == '000001' and self.platform == '01':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = False
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = True
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = True
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = True
        if self.eb_3_transaction_type == '000001' and self.platform == '02':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = False
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = True
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = True
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = True
        if self.eb_3_transaction_type == '000001' and self.platform == '03':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = True
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = True
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = True
        if self.eb_3_transaction_type == '000001' and self.platform == '04':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = True
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = True
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = True
        if self.eb_3_transaction_type == '000002' and self.platform == '01':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = False
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = True
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = True
        if self.eb_3_transaction_type == '000002' and self.platform == '02':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = False
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = True
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = True
        if self.eb_3_transaction_type == '000002' and self.platform == '03':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = True
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = True
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = True
        if self.eb_3_transaction_type == '000002' and self.platform == '04':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = True
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = True
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = True

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)
        default['name'] = new_name
        return super(EbTransaction, self).copy(default)
