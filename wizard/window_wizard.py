# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from .. import misc
import datetime
import pytz
import re

from ..ISO8583.ISO8583CNT import ISO8583CNT
from ..ISO8583.ISOErrors import *
import socket
import sys
import time


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
    platform = fields.Selection(misc.PLATFORM, default='01', required=True)
    state = fields.Selection(misc.STATE, default='c_f')
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

    # Configure the client
    serverIP = "130.10.50.15"
    serverPort = 2610
    numberEcho = 5
    timeBetweenEcho = 5  # in seconds

    bigEndian = True
    # bigEndian = False

    s = None

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
            self.flag_eb_28 = False
            self.flag_eb_32 = True
            self.flag_eb_42 = False
            self.flag_eb_43 = False
            self.flag_eb_45 = False
            self.flag_eb_48 = False
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
            self.flag_eb_28 = False
            self.flag_eb_32 = True
            self.flag_eb_42 = False
            self.flag_eb_43 = False
            self.flag_eb_45 = False
            self.flag_eb_48 = False
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
            self.flag_eb_42 = False
            self.flag_eb_43 = False
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = False
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
            self.flag_eb_42 = False
            self.flag_eb_43 = False
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = False
        if self.eb_3_transaction_type == '000002' and self.platform == '01':
            self.flag_eb_2 = True
            self.flag_eb_4 = True
            self.flag_eb_11 = False
            self.flag_eb_12 = True
            self.flag_eb_13 = True
            self.flag_eb_15 = False
            self.flag_eb_19 = False
            self.flag_eb_23 = True
            self.flag_eb_28 = False
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = False
            self.flag_eb_48 = False
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
            self.flag_eb_28 = False
            self.flag_eb_32 = True
            self.flag_eb_42 = True
            self.flag_eb_43 = True
            self.flag_eb_45 = False
            self.flag_eb_48 = False
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
            self.flag_eb_43 = False
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = False
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
            self.flag_eb_43 = False
            self.flag_eb_45 = True
            self.flag_eb_48 = True
            self.flag_eb_49 = False


    @api.multi
    def consult(self):
        self._check_num()

        message = self.createMessage(3, 'F')
        self.connect()
        self.sendMessage(message, 3, 'F')

        consult = self.env['eb.transaction']
        consult.create({'eb_2_service_identifier':self.eb_2_service_identifier,
                        'eb_3_transaction_type':self.eb_3_transaction_type,
                        'eb_12_local_transaction_time':self.eb_12_local_transaction_time})
        self.eb_3_transaction_type = '000002'

        # ubicar este codigo en el close del wizard
        #if self.s is not None:
            #self.s.close()

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

        #message = self.createMessage(2, 'F')
        #self.connect()
        #self.sendMessage(message, 2, 'F')

        back = self.env['eb.transaction']
        back.create({'eb_2_service_identifier':self.eb_2_service_identifier,
                        'eb_3_transaction_type':self.eb_3_transaction_type,
                        'eb_12_local_transaction_time':self.eb_12_local_transaction_time})
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

        #message = self.createMessage(1, 'F')
        #self.connect()
        #self.sendMessage(message, 1, 'F')

        pay = self.env['eb.transaction']
        pay.create({'eb_2_service_identifier':self.eb_2_service_identifier,
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

    def createMessage(self, transactionType, platformType=None):
        # get new object
        p = ISO8583CNT()
        # some string describing the transation type
        transation = "200"
        p.setTransationType(transation)
        # Is the same that:
        # p.setMTI(transation)

        if transactionType == 3:
            p.setBit(2, self.eb_2_service_identifier)
            p.setBit(3, self.eb_3_transaction_type)
            p.setBit(12, self.eb_12_local_transaction_time)
            p.setBit(13, self.eb_13_local_transaction_date)
            p.setBit(19, self.eb_19_consult_criterion)
            p.setBit(23, self.eb_23_service_type)
            p.setBit(32, self.eb_32_setting_id.eb_32_acquirer_institution)
            p.setBit(33, self.eb_32_setting_id.eb_33_agency_code)
            p.setBit(34, self.eb_32_setting_id.eb_34_cashier)
            p.setBit(37, self.eb_32_setting_id.eb_37_acquirer_sequence)
            p.setBit(41, self.eb_32_setting_id.eb_41_terminal)

        elif transactionType == 2:
            p.setBit(2, self.eb_2_service_identifier)
            p.setBit(3, self.eb_3_transaction_type)
            p.setBit(4, self.eb_3_transaction_type)
            if platformType == 'V' or platformType == 'C':
                p.setBit(11, self.eb_12_local_transaction_time)
            p.setBit(12, self.eb_13_local_transaction_date)
            p.setBit(13, self.eb_19_consult_criterion)
            p.setBit(23, self.eb_23_service_type)
            if platformType == 'V' or platformType == 'C':
                p.setBit(28, self.eb_32_setting_id)
            p.setBit(32, self.eb_32_setting_id)
            p.setBit(33, self.eb_32_setting_id.eb_33_agency_code)
            if platformType == 'F' or platformType == 'M':
                p.setBit(34, self.eb_32_setting_id.eb_34_cashier)
                p.setBit(37, self.eb_32_setting_id.eb_37_acquirer_sequence)
            p.setBit(41, 986)
            p.setBit(42, 986)
            if platformType == 'F' or platformType == 'M':
                p.setBit(43, 986)
            if platformType == 'V' or platformType == 'C':
                p.setBit(45, self.eb_45_name_lastname)
                p.setBit(48, 986)
            if platformType == 'F' or platformType == 'M':
                p.setBit(49, 986)
        elif transactionType == 1:
            p.setBit(2, self.eb_2_service_identifier)
            p.setBit(3, self.eb_3_transaction_type)
            p.setBit(4, self.eb_12_local_transaction_time)
            if platformType == 'V' or platformType == 'C':
                p.setBit(11, self.eb_13_local_transaction_date)
            p.setBit(12, self.eb_19_consult_criterion)
            p.setBit(13, self.eb_23_service_type)
            if platformType == 'F' or platformType == 'M':
                p.setBit(15, self.eb_23_service_type)
            p.setBit(23, self.eb_23_service_type)
            if platformType == 'V' or platformType == 'C':
                p.setBit(28, self.eb_23_service_type)
            p.setBit(32, self.eb_32_setting_id)
            p.setBit(33, self.eb_32_setting_id.eb_33_agency_code)
            if platformType == 'F' or platformType == 'M':
                p.setBit(34, self.eb_32_setting_id.eb_34_cashier)
            p.setBit(37, self.eb_32_setting_id.eb_37_acquirer_sequence)
            p.setBit(41, 986)
            if platformType == 'V' or platformType == 'C':
                p.setBit(45, self.eb_45_name_lastname)
                p.setBit(48, 986)
            if platformType == 'F' or platformType == 'M':
                p.setBit(49, 986)
        else:
            p.setBit(7, self.eb_2_service_identifier)
            p.setBit(11, self.eb_3_transaction_type)
            p.setBit(18, self.eb_12_local_transaction_time)
            p.setBit(70, 986)
        return  p.getRawIso()

    def connect(self):
        for res in socket.getaddrinfo(self.serverIP, self.serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.s = socket.socket(af, socktype, proto)
            except socket.error, msg:
                self.s = None
                continue
            try:
                self.s.connect(sa)
            except socket.error, msg:
                self.s.close()
                self.s = None
                continue
            break
        if self.s is None:
            print ('Could not connect :(')

    def sendMessage(self, message, transactionType, platformType):
        try:
            self.s.send(message)
            ans = self.s.recv(2048)
            isoAns = ISO8583CNT()
            isoAns.setIsoContent(ans)
            isoAns.getRawIso()
            if transactionType == 3:
                isoAns.getBit(4)
                isoAns.getBit(18)
            elif transactionType == 2:
                isoAns.getBit(18)
            elif transactionType == 1:
                isoAns.getBit(18)
                isoAns.getBit(42)
            else:
                isoAns.getBit(18)
        except InvalidIso8583, ii:
            print ii
