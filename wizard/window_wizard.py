# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from .. import misc
import datetime
import pytz
import re


class WindowWizard(models.TransientModel):

    _name = 'eb.window.wizard'
    _description = 'Window wizard'

    name = fields.Char()
    eb_2_service_identifier = fields.Char(size=19, required=True)
    eb_3_transaction_type = fields.Selection(misc.TRANSACTION_TYPE, default='000003', required=True)
    eb_4_total_value = fields.Float(digits=(18, 2))
    eb_7_date_time = fields.Char()
    eb_11_location_code = fields.Char(size=6, default='010150')
    eb_11_sequential = fields.Char()
    eb_12_local_transaction_time = fields.Char(size=6, compute='_compute_time_now')
    eb_13_local_transaction_date = fields.Char(size=8, compute='_compute_date_now')
    eb_15_compensation_date = fields.Char(size=8, compute='_compute_date_now')
    eb_19_consult_criterion = fields.Selection(misc.CONSULT_CRITERION, default='001')
    eb_23_service_type = fields.Selection(misc.SERVICE_TYPE, default='000', required=True)
    eb_28_doc = fields.Char(size=20)
    eb_32_setting_id = fields.Many2one('eb.setting', required=True)
    eb_42_pay_id = fields.Char(size=12)
    eb_43_back_reason = fields.Selection(misc.BACK_REASON, default='02')
    eb_45_name_lastname = fields.Char(size=35, default='Luis Enrique Perez Lopez')
    eb_48_address = fields.Char(size=200, default='Polaris')
    eb_49_currency_type = fields.Char(size=3, default='USD')
    eb_70_administrative_transaction_code = fields.Char()
    mit = fields.Selection(misc.MIT)
    telephony = fields.Char()
    response = fields.Char()

    @api.one
    @api.onchange('eb_2_service_identifier','eb_11_location_code','eb_42_pay_id')
    def _check_num(self):
        if self.eb_2_service_identifier:
            try:
                int(self.eb_2_service_identifier)
            except ValueError:
                raise ValidationError("NAN " + self.eb_2_service_identifier +
                                      " -> " + self._fields['eb_2_service_identifier']._column_string)
        if self.eb_11_location_code:
            try:
                int(self.eb_11_location_code)
            except ValueError:
                raise ValidationError("NAN " + self.eb_11_location_code +
                                      " -> " + self._fields['eb_11_location_code']._column_string)
        if self.eb_42_pay_id:
            try:
                int(self.eb_42_pay_id)
            except ValueError:
                raise ValidationError("NAN " + self.eb_42_pay_id +
                                      " -> " + self._fields['eb_42_pay_id']._column_string)

    @api.one
    @api.onchange('eb_28_doc','eb_48_address')
    def _check_alphanum(self):
        if self.eb_28_doc:
            if not self.eb_28_doc.isalnum():
                raise ValidationError("NAALN " + self.eb_28_doc +
                                      " -> " + self._fields['eb_28_doc']._column_string)
        if self.eb_48_address:
            if not self.eb_48_address.isalnum():
                raise ValidationError("NAALN " + self.eb_48_address +
                                      " -> " + self._fields['eb_48_address']._column_string)

    @api.one
    @api.onchange('eb_45_name_lastname')
    def _check_a(self):
        if self.eb_45_name_lastname:
            r = re.compile("^[a-zA-Z0-9 ]*$")
            if not r.match(self.eb_45_name_lastname):
                raise ValidationError("Not alphanumeric with space " + self.eb_45_name_lastname +
                                      " -> " + self._fields['eb_45_name_lastname']._column_string)

    @api.one
    @api.onchange('eb_11_location_code','eb_49_currency_type')
    def _check_size(self):
        if self.eb_11_location_code:
            if len(self.eb_11_location_code) != 6:
                raise ValidationError("Check size " + self.eb_11_location_code +
                                      " -> " + self._fields['eb_11_location_code']._column_string)
        if self.eb_49_currency_type:
            if len(self.eb_49_currency_type) != 3:
                raise ValidationError("Check size " + self.eb_49_currency_type +
                                      " -> " + self._fields['eb_49_currency_type']._column_string)

    @api.one
    @api.depends('eb_3_transaction_type')
    def _compute_time_now(self):
        tz = pytz.timezone('America/Bogota')
        self.eb_12_local_transaction_time = str(datetime.datetime.now(tz).hour).zfill(2) + \
                                            str(datetime.datetime.now(tz).minute).zfill(2) + str(datetime.datetime.now(tz).second).zfill(2)

    @api.one
    @api.depends('eb_3_transaction_type')
    def _compute_date_now(self):
        tz = pytz.timezone('America/Bogota')
        self.eb_13_local_transaction_date = str(datetime.datetime.now(tz).year).zfill(4) \
                                            + str(datetime.datetime.now(tz).month).zfill(2) + str(datetime.datetime.now(tz).day).zfill(2)
        self.eb_15_compensation_date = self.eb_13_local_transaction_date


    @api.multi
    def consult(self):
        self._check_num()
        consult = self.env['eb.transaction']
        consult.create({'eb_2_service_identifier':self.eb_2_service_identifier,
                        'eb_3_transaction_type':self.eb_3_transaction_type,
                        'eb_12_local_transaction_time':self.eb_12_local_transaction_time})
        self.eb_3_transaction_type = '000001'
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eb.window.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def back(self):
        self._check_num()
        self._check_alphanum()
        self._check_size()
        self._check_a()
        back = self.env['eb.transaction']
        back.create({'eb_2_service_identifier':self.eb_2_service_identifier,
                     'eb_3_transaction_type':self.eb_3_transaction_type,
                     'eb_12_local_transaction_time':self.eb_12_local_transaction_time})
        self.eb_2_service_identifier = ''
        self.eb_32_setting_id = ''
        self.eb_3_transaction_type = '000003'
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eb.window.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def pay(self):
        self._check_num()
        self._check_alphanum()
        self._check_size()
        self._check_a()
        pay = self.env['eb.transaction']
        pay.create({'eb_2_service_identifier':self.eb_2_service_identifier,
                    'eb_3_transaction_type':self.eb_3_transaction_type,
                    'eb_12_local_transaction_time':self.eb_12_local_transaction_time})
        self.eb_3_transaction_type = '000002'
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eb.window.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }