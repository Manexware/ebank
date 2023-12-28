# -*- coding: utf-8 -*-
from ..ISO8583.ISO8583CNT import ISO8583CNT
from ..ISO8583.ISOErrors import *
import socket
from odoo import models, fields, api


TRANSACTION_TYPE = [
    ('000001', 'Pay'),
    ('000002', 'Back'),
    ('000003', 'Consult'),
]

CONSULT_CRITERION = [
    ('001', 'by telephone number'),
    ('002', 'by financial account'),
]

SERVICE_TYPE = [
    ('000', 'TOTAL PAY'),
    ('001', 'FIXED'),
    ('002', 'MOBILE'),
    ('003', 'FIXED INTERNET'),
    ('004', 'TV'),
    ('005', 'CNT RECHARGE MOBILE'),
    ('006', 'CDMA 450 FIXED RECHARGE'),
]

BACK_REASON = [
    ('02', 'annulment'),
    ('03', 'timeout'),
]
PLATFORM = [
    ('01', 'Fixed'),
    ('02', 'Mobile'),
    ('03', 'VTA'),
    ('04', 'CDMA 450'),
]
STATE = [
    ('c_f', "c-f"),
    ('c_m', "c-m"),
    ('p_f', "p_f"),
    ('p_m', "p_m"),
    ('p_v', "p_v"),
    ('p_c', "p_c"),
    ('r_f', "r_f"),
    ('r_m', "r_m"),
    ('r_v', "r_v"),
    ('r_c', "r_c"),
]


def create_consultation_message(self):
    iso = ISO8583CNT()
    transaction = "200"
    iso.set_transaction_type(transaction)
    iso.set_bit(2, self.ebank_2_service_identifier)
    iso.set_bit(3, self.ebank_3_transaction_type)
    iso.set_bit(12, self.ebank_12_local_transaction_time)
    iso.set_bit(13, self.ebank_13_local_transaction_date)
    iso.set_bit(19, self.ebank_19_consult_criterion)
    iso.set_bit(23, self.ebank_23_service_type)
    iso.set_bit(32, self.ebank_32_setting_id.ebank_32_acquirer_institution)
    iso.set_bit(33, self.ebank_32_setting_id.ebank_33_agency_code)
    iso.set_bit(34, self.ebank_32_setting_id.ebank_34_cashier)
    iso.set_bit(37, self.ebank_32_setting_id.ebank_37_acquirer_sequence)
    iso.set_bit(41, self.ebank_32_setting_id.ebank_41_terminal)
    return iso.get_raw_iso()


def create_reverse_message(self, platform_type=None):
    iso = ISO8583CNT()
    transaction = "200"
    iso.set_transaction_type(transaction)
    iso.set_bit(2, self.ebank_2_service_identifier)
    iso.set_bit(3, self.ebank_3_transaction_type)
    iso.set_bit(4, self.ebank_3_transaction_type)
    if platform_type == 'V' or platform_type == 'C':
        iso.set_bit(11, self.ebank_12_local_transaction_time)
    iso.set_bit(12, self.ebank_13_local_transaction_date)
    iso.set_bit(13, self.ebank_19_consult_criterion)
    iso.set_bit(23, self.ebank_23_service_type)
    if platform_type == 'V' or platform_type == 'C':
        iso.set_bit(28, self.ebank_32_setting_id)
    iso.set_bit(32, self.ebank_32_setting_id.ebank_32_acquirer_institution)
    iso.set_bit(33, self.ebank_32_setting_id.ebank_33_agency_code)
    if platform_type == 'F' or platform_type == 'M':
        iso.set_bit(34, self.ebank_32_setting_id.ebank_34_cashier)
        iso.set_bit(37, self.ebank_32_setting_id.ebank_37_acquirer_sequence)
    iso.set_bit(41, 986)
    iso.set_bit(42, 986)
    if platform_type == 'F' or platform_type == 'M':
        iso.set_bit(43, 986)
    if platform_type == 'V' or platform_type == 'C':
        iso.set_bit(45, self.ebank_45_name_lastname)
        iso.set_bit(48, 986)
    if platform_type == 'F' or platform_type == 'M':
        iso.set_bit(49, 986)
    return iso.get_raw_iso()


def create_payment_message(self, platform_type=None):
    p = ISO8583CNT()
    transaction = "200"
    p.set_transaction_type(transaction)
    p.set_bit(2, self.ebank_2_service_identifier)
    p.set_bit(3, self.ebank_3_transaction_type)
    p.set_bit(4, self.ebank_12_local_transaction_time)
    if platform_type == 'V' or platform_type == 'C':
        p.set_bit(11, self.ebank_13_local_transaction_date)
    p.set_bit(12, self.ebank_19_consult_criterion)
    p.set_bit(13, self.ebank_23_service_type)
    if platform_type == 'F' or platform_type == 'M':
        p.set_bit(15, self.ebank_23_service_type)
        p.set_bit(23, self.ebank_23_service_type)
    if platform_type == 'V' or platform_type == 'C':
        p.set_bit(28, self.ebank_23_service_type)
    p.set_bit(32, self.ebank_32_setting_id.ebank_32_acquirer_institution)
    p.set_bit(33, self.ebank_32_setting_id.ebank_33_agency_code)
    if platform_type == 'F' or platform_type == 'M':
        p.set_bit(34, self.ebank_32_setting_id.ebank_34_cashier)
    p.set_bit(37, self.ebank_32_setting_id.ebank_37_acquirer_sequence)
    p.set_bit(41, 986)
    if platform_type == 'V' or platform_type == 'C':
        p.set_bit(45, self.ebank_45_name_lastname)
        p.set_bit(48, 986)
    if platform_type == 'F' or platform_type == 'M':
        p.set_bit(49, 986)
    else:
        p.set_bit(7, self.ebank_2_service_identifier)
        p.set_bit(11, self.ebank_3_transaction_type)
        p.set_bit(18, self.ebank_12_local_transaction_time)
        p.set_bit(70, 986)
    return p.get_raw_iso()


def create_control_message(self):
    p = ISO8583CNT()
    transaction = "200"
    p.set_transaction_type(transaction)
    p.set_bit(7, self.ebank_2_service_identifier)
    p.set_bit(11, self.ebank_3_transaction_type)
    p.set_bit(18, self.ebank_12_local_transaction_time)
    p.set_bit(70, 986)
    return p.get_raw_iso()


def connect(self):
    for res in socket.getaddrinfo(self.serverIP, self.serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, sock_type, proto, canon_name, sa = res
        try:
            self.s = socket.socket(af, sock_type, proto)
        except socket.error as msg:
            self.s = None
            continue
        try:
            self.s.connect(sa)
        except socket.error as msg:
            self.s.close()
            self.s = None
            continue
        break
    if self.s is None:
        print ('Could not connect :(')
        result = False
    else:
        result = True
    return result


def send_message(self, message, transaction_type):
    try:
        code = "ERROR"
        data = message + '\n'
        self.s.send(data)
        ans = self.s.recv(2048)
        if ans:
            if ans != data:
                iso_ans = ISO8583CNT()
                iso_ans.set_iso_content(ans)
                #self.response = isoAns.getRawIso()
                self.response = iso_ans.get_bit(18)
                if transaction_type == 3:
                    self.ebank_4_total_value = iso_ans.get_bit(4)
                elif transaction_type == 1:
                    self.ebank_42_pay_id = iso_ans.get_bit(42)
            else:
                self.response = code
        else:
            self.response = code
    except invalidIso8583 as ii:
        print(ii)


class EBankTransaction(models.Model):
    _name = 'ebank.transaction'
    _description = 'Transaction'

    name = fields.Char()
    ebank_2_service_identifier = fields.Char(size=19)
    ebank_3_transaction_type = fields.Selection(TRANSACTION_TYPE)
    platform = fields.Selection(PLATFORM, default='01', required=True)
    ebank_4_total_value = fields.Float(digits=(18, 2))
    ebank_7_date_time = fields.Char()
    ebank_11_location_code = fields.Char(size=6)
    ebank_11_sequential = fields.Char()
    ebank_12_local_transaction_time = fields.Char(size=6)
    ebank_13_local_transaction_date = fields.Char(size=8)
    ebank_15_compensation_date = fields.Char(size=8)
    ebank_19_consult_criterion = fields.Selection(CONSULT_CRITERION)
    ebank_23_service_type = fields.Selection(SERVICE_TYPE)
    ebank_28_doc = fields.Char(size=20)
    ebank_32_setting_id = fields.Many2one('ebank.setting')
    ebank_42_pay_id = fields.Char(size=12)
    ebank_43_back_reason = fields.Selection(BACK_REASON)
    ebank_45_name_lastname = fields.Char(size=35)
    ebank_48_address = fields.Char(size=200)
    ebank_49_currency_type = fields.Char(size=3)
    ebank_70_administrative_transaction_code = fields.Char()
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

    _order = 'name'

    _sql_constraints = [
        ('name_uk', 'unique(name)', 'Transaction must be unique'),
    ]

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
        return super(EBankTransaction, self).copy(default)
