# -*- coding: utf-8 -*-
import datetime
import re

import pytz

from odoo import models, fields, api
from odoo.addons.teller.models.TellerTransaction import (create_reverse_message, connect, send_message,
                                                         create_payment_message, create_consultation_message, PLATFORM,
                                                         STATE, SERVICE_TYPE, CONSULT_CRITERION,
                                                         BACK_REASON, TRANSACTION_TYPE)
from odoo.exceptions import ValidationError


class TellerWizard(models.TransientModel):
    _name = 'teller.wizard'
    _description = 'Teller wizard'

    name = fields.Char()
    f2_service_identifier = fields.Char(size=19, required=True, default='62464524')
    f3_transaction_type = fields.Selection(TRANSACTION_TYPE, default='000003', required=True)
    f4_total_value = fields.Float(digits=(18, 2))
    f7_date_time = fields.Char()
    f11_location_code = fields.Char(size=6, default='010150')
    f11_sequential = fields.Char()
    f12_local_transaction_time = fields.Char(size=6, compute='_compute_time_now')
    f13_local_transaction_date = fields.Char(size=8, compute='_compute_date_now')
    f15_compensation_date = fields.Char(size=8, compute='_compute_date_now')
    f19_consult_criterion = fields.Selection(CONSULT_CRITERION, default='001')
    f23_service_type = fields.Selection(SERVICE_TYPE, default='000', required=True)
    f28_doc = fields.Char(size=20)
    f32_setting_id = fields.Many2one('teller.setting', required=True)
    f42_pay_id = fields.Char(size=12)
    f43_back_reason = fields.Selection(BACK_REASON, default='02')
    f45_name_lastname = fields.Char(size=35, default='Luis Enrique Perez Lopez')
    f48_address = fields.Char(size=200, default='Polaris')
    f49_currency_type = fields.Char(size=3, default='USD')
    f70_administrative_transaction_code = fields.Char()
    platform = fields.Selection(PLATFORM, default='01', required=True)
    state = fields.Selection(STATE, default='c_f')
    flag_f2 = fields.Boolean(compute='_set_flag', default=False)
    flag_f4 = fields.Boolean(compute='_set_flag', default=False)
    flag_f7 = fields.Boolean(compute='_set_flag', default=False)
    flag_f11 = fields.Boolean(compute='_set_flag', default=False)
    flag_f12 = fields.Boolean(compute='_set_flag', default=False)
    flag_f13 = fields.Boolean(compute='_set_flag', default=False)
    flag_f15 = fields.Boolean(compute='_set_flag', default=False)
    flag_f19 = fields.Boolean(compute='_set_flag', default=False)
    flag_f23 = fields.Boolean(compute='_set_flag', default=False)
    flag_f28 = fields.Boolean(compute='_set_flag', default=False)
    flag_f32 = fields.Boolean(compute='_set_flag', default=False)
    flag_f42 = fields.Boolean(compute='_set_flag', default=False)
    flag_f43 = fields.Boolean(compute='_set_flag', default=False)
    flag_f45 = fields.Boolean(compute='_set_flag', default=False)
    flag_f48 = fields.Boolean(compute='_set_flag', default=False)
    flag_f49 = fields.Boolean(compute='_set_flag', default=False)
    flag_f70 = fields.Boolean(compute='_set_flag', default=False)

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

    @api.onchange('f2_service_identifier', 'f11_location_code', 'f42_pay_id')
    def _check_num(self):
        if self.f2_service_identifier:
            try:
                int(self.f2_service_identifier)
            except ValueError:
                raise ValidationError("NAN " + self.f2_service_identifier +
                                      " -> " + self._fields['f2_service_identifier']._column_string)
        if self.f11_location_code:
            try:
                int(self.f11_location_code)
            except ValueError:
                raise ValidationError("NAN " + self.f11_location_code +
                                      " -> " + self._fields['f11_location_code']._column_string)
        if self.f42_pay_id:
            try:
                int(self.f42_pay_id)
            except ValueError:
                raise ValidationError("NAN " + self.f42_pay_id +
                                      " -> " + self._fields['f42_pay_id']._column_string)

    @api.onchange('f28_doc', 'f48_address')
    def _check_alphanum(self):
        if self.f28_doc:
            if not self.f28_doc.isalnum():
                raise ValidationError("NAALN " + self.f28_doc +
                                      " -> " + self._fields['f28_doc']._column_string)
        if self.f48_address:
            if not self.f48_address.isalnum():
                raise ValidationError("NAALN " + self.f48_address +
                                      " -> " + self._fields['f48_address']._column_string)

    @api.onchange('f45_name_lastname')
    def _check_a(self):
        if self.f45_name_lastname:
            r = re.compile("^[a-zA-Z0-9 ]*$")
            if not r.match(self.f45_name_lastname):
                raise ValidationError("Not alphanumeric with space " + self.f45_name_lastname +
                                      " -> " + self._fields['f45_name_lastname']._column_string)

    @api.onchange('f11_location_code', 'f49_currency_type')
    def _check_size(self):
        if self.f11_location_code:
            if len(self.f11_location_code) != 6:
                raise ValidationError("Check size " + self.f11_location_code +
                                      " -> " + self._fields['f11_location_code']._column_string)
        if self.f49_currency_type:
            if len(self.f49_currency_type) != 3:
                raise ValidationError("Check size " + self.f49_currency_type +
                                      " -> " + self._fields['f49_currency_type']._column_string)

    @api.depends('f3_transaction_type')
    def _compute_time_now(self):
        tz = pytz.timezone('America/Bogota')
        self.f12_local_transaction_time = str(datetime.datetime.now(tz).hour).zfill(2) + str(
            datetime.datetime.now(tz).minute).zfill(2) + str(
            datetime.datetime.now(tz).second).zfill(2)

    @api.depends('f3_transaction_type')
    def _compute_date_now(self):
        tz = pytz.timezone('America/Bogota')
        self.f13_local_transaction_date = str(datetime.datetime.now(tz).year).zfill(4) + str(
            datetime.datetime.now(tz).month).zfill(2) + str(
            datetime.datetime.now(tz).day).zfill(2)
        self.f15_compensation_date = self.f13_local_transaction_date

    @api.depends('f3_transaction_type', 'platform')
    def _set_flag(self):
        if self.f3_transaction_type == '000003' and self.platform == '01':
            self.flag_f2 = True
            self.flag_f4 = False
            self.flag_f11 = False
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = False
            self.flag_f19 = True
            self.flag_f23 = True
            self.flag_f28 = False
            self.flag_f32 = True
            self.flag_f42 = False
            self.flag_f43 = False
            self.flag_f45 = False
            self.flag_f48 = False
            self.flag_f49 = False
        if self.f3_transaction_type == '000003' and self.platform == '02':
            self.flag_f2 = True
            self.flag_f4 = False
            self.flag_f11 = False
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = False
            self.flag_f19 = True
            self.flag_f23 = True
            self.flag_f28 = False
            self.flag_f32 = True
            self.flag_f42 = False
            self.flag_f43 = False
            self.flag_f45 = False
            self.flag_f48 = False
            self.flag_f49 = False
        if self.f3_transaction_type == '000003' and self.platform == '03':
            self.flag_f2 = False
            self.flag_f4 = False
            self.flag_f11 = False
            self.flag_f12 = False
            self.flag_f13 = False
            self.flag_f15 = False
            self.flag_f19 = False
            self.flag_f23 = False
            self.flag_f28 = False
            self.flag_f32 = False
            self.flag_f42 = False
            self.flag_f43 = False
            self.flag_f45 = False
            self.flag_f48 = False
            self.flag_f49 = False
        if self.f3_transaction_type == '000003' and self.platform == '04':
            self.flag_f2 = False
            self.flag_f4 = False
            self.flag_f11 = False
            self.flag_f12 = False
            self.flag_f13 = False
            self.flag_f15 = False
            self.flag_f19 = False
            self.flag_f23 = False
            self.flag_f28 = False
            self.flag_f32 = False
            self.flag_f42 = False
            self.flag_f43 = False
            self.flag_f45 = False
            self.flag_f48 = False
            self.flag_f49 = False
        if self.f3_transaction_type == '000001' and self.platform == '01':
            self.flag_f2 = True
            self.flag_f4 = True
            self.flag_f11 = False
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = True
            self.flag_f19 = False
            self.flag_f23 = True
            self.flag_f28 = False
            self.flag_f32 = True
            self.flag_f42 = False
            self.flag_f43 = False
            self.flag_f45 = False
            self.flag_f48 = False
            self.flag_f49 = True
        if self.f3_transaction_type == '000001' and self.platform == '02':
            self.flag_f2 = True
            self.flag_f4 = True
            self.flag_f11 = False
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = True
            self.flag_f19 = False
            self.flag_f23 = True
            self.flag_f28 = False
            self.flag_f32 = True
            self.flag_f42 = False
            self.flag_f43 = False
            self.flag_f45 = False
            self.flag_f48 = False
            self.flag_f49 = True
        if self.f3_transaction_type == '000001' and self.platform == '03':
            self.flag_f2 = True
            self.flag_f4 = True
            self.flag_f11 = True
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = False
            self.flag_f19 = False
            self.flag_f23 = True
            self.flag_f28 = True
            self.flag_f32 = True
            self.flag_f42 = False
            self.flag_f43 = False
            self.flag_f45 = True
            self.flag_f48 = True
            self.flag_f49 = False
        if self.f3_transaction_type == '000001' and self.platform == '04':
            self.flag_f2 = True
            self.flag_f4 = True
            self.flag_f11 = True
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = False
            self.flag_f19 = False
            self.flag_f23 = True
            self.flag_f28 = True
            self.flag_f32 = True
            self.flag_f42 = False
            self.flag_f43 = False
            self.flag_f45 = True
            self.flag_f48 = True
            self.flag_f49 = False
        if self.f3_transaction_type == '000002' and self.platform == '01':
            self.flag_f2 = True
            self.flag_f4 = True
            self.flag_f11 = False
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = False
            self.flag_f19 = False
            self.flag_f23 = True
            self.flag_f28 = False
            self.flag_f32 = True
            self.flag_f42 = True
            self.flag_f43 = True
            self.flag_f45 = False
            self.flag_f48 = False
            self.flag_f49 = True
        if self.f3_transaction_type == '000002' and self.platform == '02':
            self.flag_f2 = True
            self.flag_f4 = True
            self.flag_f11 = False
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = False
            self.flag_f19 = False
            self.flag_f23 = True
            self.flag_f28 = False
            self.flag_f32 = True
            self.flag_f42 = True
            self.flag_f43 = True
            self.flag_f45 = False
            self.flag_f48 = False
            self.flag_f49 = True
        if self.f3_transaction_type == '000002' and self.platform == '03':
            self.flag_f2 = True
            self.flag_f4 = True
            self.flag_f11 = True
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = False
            self.flag_f19 = False
            self.flag_f23 = True
            self.flag_f28 = True
            self.flag_f32 = True
            self.flag_f42 = True
            self.flag_f43 = False
            self.flag_f45 = True
            self.flag_f48 = True
            self.flag_f49 = False
        if self.f3_transaction_type == '000002' and self.platform == '04':
            self.flag_f2 = True
            self.flag_f4 = True
            self.flag_f11 = True
            self.flag_f12 = True
            self.flag_f13 = True
            self.flag_f15 = False
            self.flag_f19 = False
            self.flag_f23 = True
            self.flag_f28 = True
            self.flag_f32 = True
            self.flag_f42 = True
            self.flag_f43 = False
            self.flag_f45 = True
            self.flag_f48 = True
            self.flag_f49 = False

    def consult(self):
        self._check_num()

        message = create_consultation_message(self)
        connect(self)
        send_message(self, message, 3)

        consult = self.env['teller.transaction']
        consult.create({'f2_service_identifier': self.f2_service_identifier,
                        'f3_transaction_type': self.f3_transaction_type,
                        'f12_local_transaction_time': self.f12_local_transaction_time})
        self.f3_transaction_type = '000001'
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'teller.wizard',
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

        message = create_reverse_message(self, 2)
        connect(self)
        send_message(message, 2, 'F')

        back = self.env['teller.transaction']
        back.create({'f2_service_identifier': self.f2_service_identifier,
                     'f3_transaction_type': self.f3_transaction_type,
                     'f12_local_transaction_time': self.f12_local_transaction_time})
        self.f3_transaction_type = '000003'

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'teller.wizard',
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

        message = create_payment_message(self, 1)
        connect(self)
        send_message(message, 1, 'F')

        pay = self.env['teller.transaction']
        pay.create({'f2_service_identifier': self.f2_service_identifier,
                    'f3_transaction_type': self.f3_transaction_type,
                    'f12_local_transaction_time': self.f12_local_transaction_time})
        self.f3_transaction_type = '000001'

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'teller.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
