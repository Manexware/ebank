# -*- coding: utf-8 -*-
from ..ISO8583.ISO8583CNT import ISO8583CNT
from ..ISO8583.ISOErrors import *
import socket


def create_consultation_message(self):
    iso = ISO8583CNT()
    transaction = "200"
    iso.setTransationType(transaction)
    iso.setBit(2, self.eb_2_service_identifier)
    iso.setBit(3, self.eb_3_transaction_type)
    iso.setBit(12, self.eb_12_local_transaction_time)
    iso.setBit(13, self.eb_13_local_transaction_date)
    iso.setBit(19, self.eb_19_consult_criterion)
    iso.setBit(23, self.eb_23_service_type)
    iso.setBit(32, self.eb_32_setting_id.eb_32_acquirer_institution)
    iso.setBit(33, self.eb_32_setting_id.eb_33_agency_code)
    iso.setBit(34, self.eb_32_setting_id.eb_34_cashier)
    iso.setBit(37, self.eb_32_setting_id.eb_37_acquirer_sequence)
    iso.setBit(41, self.eb_32_setting_id.eb_41_terminal)
    return iso.getRawIso()


def create_reverse_message(self, platformType=None):
    iso = ISO8583CNT()
    transaction = "200"
    iso.setTransationType(transaction)
    iso.setBit(2, self.eb_2_service_identifier)
    iso.setBit(3, self.eb_3_transaction_type)
    iso.setBit(4, self.eb_3_transaction_type)
    if platformType == 'V' or platformType == 'C':
        iso.setBit(11, self.eb_12_local_transaction_time)
    iso.setBit(12, self.eb_13_local_transaction_date)
    iso.setBit(13, self.eb_19_consult_criterion)
    iso.setBit(23, self.eb_23_service_type)
    if platformType == 'V' or platformType == 'C':
        iso.setBit(28, self.eb_32_setting_id)
    iso.setBit(32, self.eb_32_setting_id.eb_32_acquirer_institution)
    iso.setBit(33, self.eb_32_setting_id.eb_33_agency_code)
    if platformType == 'F' or platformType == 'M':
        iso.setBit(34, self.eb_32_setting_id.eb_34_cashier)
        iso.setBit(37, self.eb_32_setting_id.eb_37_acquirer_sequence)
    iso.setBit(41, 986)
    iso.setBit(42, 986)
    if platformType == 'F' or platformType == 'M':
        iso.setBit(43, 986)
    if platformType == 'V' or platformType == 'C':
        iso.setBit(45, self.eb_45_name_lastname)
        iso.setBit(48, 986)
    if platformType == 'F' or platformType == 'M':
        iso.setBit(49, 986)
    return iso.getRawIso()


def create_payment_message(self, platformType=None):
    p = ISO8583CNT()
    transaction = "200"
    p.setTransationType(transaction)
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
    p.setBit(32, self.eb_32_setting_id.eb_32_acquirer_institution)
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
    return p.getRawIso()


def create_control_message(self):
    p = ISO8583CNT()
    transaction = "200"
    p.setTransationType(transaction)
    p.setBit(7, self.eb_2_service_identifier)
    p.setBit(11, self.eb_3_transaction_type)
    p.setBit(18, self.eb_12_local_transaction_time)
    p.setBit(70, 986)
    return p.getRawIso()


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
                isoAns = ISO8583CNT()
                isoAns.setIsoContent(ans)
                #self.response = isoAns.getRawIso()
                self.response = isoAns.getBit(18)
                if transaction_type == 3:
                    self.eb_4_total_value = isoAns.getBit(4)
                elif transaction_type == 1:
                    self.eb_42_pay_id = isoAns.getBit(42)
            else:
                self.response = code
        else:
            self.response = code

    except InvalidIso8583, ii:
        print ii
