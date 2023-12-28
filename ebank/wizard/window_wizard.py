# -*- coding: utf-8 -*-
import datetime
import re

import pytz

from models import ebank_transaction
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EBankWizard(models.TransientModel):
    _name = 'ebank.wizard'
    _description = 'eBank wizard'

    name = fields.Char()
    ebank_2_service_identifier = fields.Char(size=19, required=True, default='62464524')
    ebank_3_transaction_type = fields.Selection(ebank_transaction.TRANSACTION_TYPE, default='000003', required=True)
    ebank_4_total_value = fields.Float(digits=(18, 2))
    ebank_7_date_time = fields.Char()
    ebank_11_location_code = fields.Char(size=6, default='010150')
    ebank_11_sequential = fields.Char()
    ebank_12_local_transaction_time = fields.Char(size=6, compute='_compute_time_now')
    ebank_13_local_transaction_date = fields.Char(size=8, compute='_compute_date_now')
    ebank_15_compensation_date = fields.Char(size=8, compute='_compute_date_now')
    ebank_19_consult_criterion = fields.Selection(ebank_transaction.CONSULT_CRITERION, default='001')
    ebank_23_service_type = fields.Selection(ebank_transaction.SERVICE_TYPE, default='000', required=True)
    ebank_28_doc = fields.Char(size=20)
    ebank_32_setting_id = fields.Many2one('ebank.setting', required=True)
    ebank_42_pay_id = fields.Char(size=12)
    ebank_43_back_reason = fields.Selection(ebank_transaction.BACK_REASON, default='02')
    ebank_45_name_lastname = fields.Char(size=35, default='Luis Enrique Perez Lopez')
    ebank_48_address = fields.Char(size=200, default='Polaris')
    ebank_49_currency_type = fields.Char(size=3, default='USD')
    ebank_70_administrative_transaction_code = fields.Char()
    platform = fields.Selection(ebank_transaction.PLATFORM, default='01', required=True)
    state = fields.Selection(ebank_transaction.STATE, default='c_f')
    flag_ebank_2 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_4 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_7 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_11 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_12 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_13 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_15 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_19 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_23 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_28 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_32 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_42 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_43 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_45 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_48 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_49 = fields.Boolean(compute='_set_flag', default=False)
    flag_ebank_70 = fields.Boolean(compute='_set_flag', default=False)

    mit = fields.Char()
    telephony = fields.Char()
    response = fields.Char()

    # Configure the client
    # serverIP = "130.10.50.15"
    serverIP = "172.17.222.136"
    serverPort = 8899
    numberEcho = 5
    timeBetweenEcho = 5  # in seconds

    bigEndian = True
    # bigEndian = False

    s = None

    @api.onchange('ebank_2_service_identifier', 'ebank_11_location_code', 'ebank_42_pay_id')
    def _check_num(self):
        if self.ebank_2_service_identifier:
            try:
                int(self.ebank_2_service_identifier)
            except ValueError:
                raise ValidationError("NAN " + self.ebank_2_service_identifier +
                                      " -> " + self._fields['ebank_2_service_identifier']._column_string)
        if self.ebank_11_location_code:
            try:
                int(self.ebank_11_location_code)
            except ValueError:
                raise ValidationError("NAN " + self.ebank_11_location_code +
                                      " -> " + self._fields['ebank_11_location_code']._column_string)
        if self.ebank_42_pay_id:
            try:
                int(self.ebank_42_pay_id)
            except ValueError:
                raise ValidationError("NAN " + self.ebank_42_pay_id +
                                      " -> " + self._fields['ebank_42_pay_id']._column_string)

    @api.onchange('ebank_28_doc', 'ebank_48_address')
    def _check_alphanum(self):
        if self.ebank_28_doc:
            if not self.ebank_28_doc.isalnum():
                raise ValidationError("NAALN " + self.ebank_28_doc +
                                      " -> " + self._fields['ebank_28_doc']._column_string)
        if self.ebank_48_address:
            if not self.ebank_48_address.isalnum():
                raise ValidationError("NAALN " + self.ebank_48_address +
                                      " -> " + self._fields['ebank_48_address']._column_string)

    @api.onchange('ebank_45_name_lastname')
    def _check_a(self):
        if self.ebank_45_name_lastname:
            r = re.compile("^[a-zA-Z0-9 ]*$")
            if not r.match(self.ebank_45_name_lastname):
                raise ValidationError("Not alphanumeric with space " + self.ebank_45_name_lastname +
                                      " -> " + self._fields['ebank_45_name_lastname']._column_string)

    @api.onchange('ebank_11_location_code', 'ebank_49_currency_type')
    def _check_size(self):
        if self.ebank_11_location_code:
            if len(self.ebank_11_location_code) != 6:
                raise ValidationError("Check size " + self.ebank_11_location_code +
                                      " -> " + self._fields['ebank_11_location_code']._column_string)
        if self.ebank_49_currency_type:
            if len(self.ebank_49_currency_type) != 3:
                raise ValidationError("Check size " + self.ebank_49_currency_type +
                                      " -> " + self._fields['ebank_49_currency_type']._column_string)

    @api.depends('ebank_3_transaction_type')
    def _compute_time_now(self):
        tz = pytz.timezone('America/Bogota')
        self.ebank_12_local_transaction_time = str(datetime.datetime.now(tz).hour).zfill(2) + str(
            datetime.datetime.now(tz).minute).zfill(2) + str(
            datetime.datetime.now(tz).second).zfill(2)

    @api.depends('ebank_3_transaction_type')
    def _compute_date_now(self):
        tz = pytz.timezone('America/Bogota')
        self.ebank_13_local_transaction_date = str(datetime.datetime.now(tz).year).zfill(4) + str(
            datetime.datetime.now(tz).month).zfill(2) + str(
            datetime.datetime.now(tz).day).zfill(2)
        self.ebank_15_compensation_date = self.ebank_13_local_transaction_date

    @api.depends('ebank_3_transaction_type', 'platform')
    def _set_flag(self):
        if self.ebank_3_transaction_type == '000003' and self.platform == '01':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = False
            self.flag_ebank_11 = False
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = False
            self.flag_ebank_19 = True
            self.flag_ebank_23 = True
            self.flag_ebank_28 = False
            self.flag_ebank_32 = True
            self.flag_ebank_42 = False
            self.flag_ebank_43 = False
            self.flag_ebank_45 = False
            self.flag_ebank_48 = False
            self.flag_ebank_49 = False
        if self.ebank_3_transaction_type == '000003' and self.platform == '02':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = False
            self.flag_ebank_11 = False
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = False
            self.flag_ebank_19 = True
            self.flag_ebank_23 = True
            self.flag_ebank_28 = False
            self.flag_ebank_32 = True
            self.flag_ebank_42 = False
            self.flag_ebank_43 = False
            self.flag_ebank_45 = False
            self.flag_ebank_48 = False
            self.flag_ebank_49 = False
        if self.ebank_3_transaction_type == '000003' and self.platform == '03':
            self.flag_ebank_2 = False
            self.flag_ebank_4 = False
            self.flag_ebank_11 = False
            self.flag_ebank_12 = False
            self.flag_ebank_13 = False
            self.flag_ebank_15 = False
            self.flag_ebank_19 = False
            self.flag_ebank_23 = False
            self.flag_ebank_28 = False
            self.flag_ebank_32 = False
            self.flag_ebank_42 = False
            self.flag_ebank_43 = False
            self.flag_ebank_45 = False
            self.flag_ebank_48 = False
            self.flag_ebank_49 = False
        if self.ebank_3_transaction_type == '000003' and self.platform == '04':
            self.flag_ebank_2 = False
            self.flag_ebank_4 = False
            self.flag_ebank_11 = False
            self.flag_ebank_12 = False
            self.flag_ebank_13 = False
            self.flag_ebank_15 = False
            self.flag_ebank_19 = False
            self.flag_ebank_23 = False
            self.flag_ebank_28 = False
            self.flag_ebank_32 = False
            self.flag_ebank_42 = False
            self.flag_ebank_43 = False
            self.flag_ebank_45 = False
            self.flag_ebank_48 = False
            self.flag_ebank_49 = False
        if self.ebank_3_transaction_type == '000001' and self.platform == '01':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = True
            self.flag_ebank_11 = False
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = True
            self.flag_ebank_19 = False
            self.flag_ebank_23 = True
            self.flag_ebank_28 = False
            self.flag_ebank_32 = True
            self.flag_ebank_42 = False
            self.flag_ebank_43 = False
            self.flag_ebank_45 = False
            self.flag_ebank_48 = False
            self.flag_ebank_49 = True
        if self.ebank_3_transaction_type == '000001' and self.platform == '02':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = True
            self.flag_ebank_11 = False
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = True
            self.flag_ebank_19 = False
            self.flag_ebank_23 = True
            self.flag_ebank_28 = False
            self.flag_ebank_32 = True
            self.flag_ebank_42 = False
            self.flag_ebank_43 = False
            self.flag_ebank_45 = False
            self.flag_ebank_48 = False
            self.flag_ebank_49 = True
        if self.ebank_3_transaction_type == '000001' and self.platform == '03':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = True
            self.flag_ebank_11 = True
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = False
            self.flag_ebank_19 = False
            self.flag_ebank_23 = True
            self.flag_ebank_28 = True
            self.flag_ebank_32 = True
            self.flag_ebank_42 = False
            self.flag_ebank_43 = False
            self.flag_ebank_45 = True
            self.flag_ebank_48 = True
            self.flag_ebank_49 = False
        if self.ebank_3_transaction_type == '000001' and self.platform == '04':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = True
            self.flag_ebank_11 = True
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = False
            self.flag_ebank_19 = False
            self.flag_ebank_23 = True
            self.flag_ebank_28 = True
            self.flag_ebank_32 = True
            self.flag_ebank_42 = False
            self.flag_ebank_43 = False
            self.flag_ebank_45 = True
            self.flag_ebank_48 = True
            self.flag_ebank_49 = False
        if self.ebank_3_transaction_type == '000002' and self.platform == '01':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = True
            self.flag_ebank_11 = False
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = False
            self.flag_ebank_19 = False
            self.flag_ebank_23 = True
            self.flag_ebank_28 = False
            self.flag_ebank_32 = True
            self.flag_ebank_42 = True
            self.flag_ebank_43 = True
            self.flag_ebank_45 = False
            self.flag_ebank_48 = False
            self.flag_ebank_49 = True
        if self.ebank_3_transaction_type == '000002' and self.platform == '02':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = True
            self.flag_ebank_11 = False
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = False
            self.flag_ebank_19 = False
            self.flag_ebank_23 = True
            self.flag_ebank_28 = False
            self.flag_ebank_32 = True
            self.flag_ebank_42 = True
            self.flag_ebank_43 = True
            self.flag_ebank_45 = False
            self.flag_ebank_48 = False
            self.flag_ebank_49 = True
        if self.ebank_3_transaction_type == '000002' and self.platform == '03':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = True
            self.flag_ebank_11 = True
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = False
            self.flag_ebank_19 = False
            self.flag_ebank_23 = True
            self.flag_ebank_28 = True
            self.flag_ebank_32 = True
            self.flag_ebank_42 = True
            self.flag_ebank_43 = False
            self.flag_ebank_45 = True
            self.flag_ebank_48 = True
            self.flag_ebank_49 = False
        if self.ebank_3_transaction_type == '000002' and self.platform == '04':
            self.flag_ebank_2 = True
            self.flag_ebank_4 = True
            self.flag_ebank_11 = True
            self.flag_ebank_12 = True
            self.flag_ebank_13 = True
            self.flag_ebank_15 = False
            self.flag_ebank_19 = False
            self.flag_ebank_23 = True
            self.flag_ebank_28 = True
            self.flag_ebank_32 = True
            self.flag_ebank_42 = True
            self.flag_ebank_43 = False
            self.flag_ebank_45 = True
            self.flag_ebank_48 = True
            self.flag_ebank_49 = False

    def consult(self):
        self._check_num()

        message = ebank_transaction.create_consultation_message(self)
        ebank_transaction.connect(self)
        ebank_transaction.send_message(self, message, 3)

        consult = self.env['ebank.transaction']
        consult.create({'ebank_2_service_identifier': self.ebank_2_service_identifier,
                        'ebank_3_transaction_type': self.ebank_3_transaction_type,
                        'ebank_12_local_transaction_time': self.ebank_12_local_transaction_time})
        self.ebank_3_transaction_type = '000001'
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ebank.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def back(self):
        self._check_num()
        self._check_alphanum()
        self._check_size()
        self._check_a()

        message = ebank_transaction.create_reverse_message(self, 2)
        ebank_transaction.connect(self)
        ebank_transaction.send_message(message, 2, 'F')

        back = self.env['ebank.transaction']
        back.create({'ebank_2_service_identifier': self.ebank_2_service_identifier,
                     'ebank_3_transaction_type': self.ebank_3_transaction_type,
                     'ebank_12_local_transaction_time': self.ebank_12_local_transaction_time})
        self.ebank_3_transaction_type = '000003'

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ebank.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def pay(self):
        self._check_num()
        self._check_alphanum()
        self._check_size()
        self._check_a()

        message = ebank_transaction.create_payment_message(self, 1)
        ebank_transaction.connect(self)
        ebank_transaction.send_message(message, 1, 'F')

        pay = self.env['ebank.transaction']
        pay.create({'ebank_2_service_identifier': self.ebank_2_service_identifier,
                    'ebank_3_transaction_type': self.ebank_3_transaction_type,
                    'ebank_12_local_transaction_time': self.ebank_12_local_transaction_time})
        self.ebank_3_transaction_type = '000001'

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ebank.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
