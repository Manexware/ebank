# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TellerSetting(models.Model):
    _name = 'teller.setting'
    _description = 'teller setting'
    _order = 'name'

    name = fields.Char(required=True)
    f32_acquirer_institution = fields.Char(required=True, size=6)
    f33_agency_code = fields.Char(required=True, size=3)
    f34_cashier = fields.Char(required=True, size=16)
    f37_acquirer_sequence = fields.Char(required=True, size=12)
    f41_terminal = fields.Char(required=True, size=16)

    _sql_constraints = [
        ('name_uk', 'unique(name)', 'Setting must be unique'),
    ]

    @api.constrains('f32_acquirer_institution', 'f33_agency_code', 'f37_acquirer_sequence')
    def _check_num(self):
        if self.f32_acquirer_institution and self.f33_agency_code and self.f37_acquirer_sequence:
            try:
                int(self.f32_acquirer_institution)
            except ValueError:
                raise ValidationError("NAN " + self.f32_acquirer_institution +
                                      " -> " + self._fields['f32_acquirer_institution']._column_string)
            try:
                int(self.f33_agency_code)
            except ValueError:
                raise ValidationError("NAN " + self.f33_agency_code +
                                      " -> " + self._fields['f33_agency_code']._column_string)
            try:
                int(self.f37_acquirer_sequence)
            except ValueError:
                raise ValidationError("NAN " + self.f37_acquirer_sequence +
                                      " -> " + self._fields['f37_acquirer_sequence']._column_string)

    @api.constrains('f34_cashier', 'f41_terminal')
    def _check_al_num(self):
        if self.f34_cashier:
            if not self.f34_cashier.isalnum():
                raise ValidationError("NAALN " + self.f34_cashier +
                                      " -> " + self._fields['f34_cashier']._column_string)
        if self.f41_terminal:
            if not self.f41_terminal.isalnum():
                raise ValidationError("NAALN " + self.f41_terminal +
                                      " -> " + self._fields['f41_terminal']._column_string)

    @api.onchange('f32_acquirer_institution', 'f33_agency_code', 'f37_acquirer_sequence')
    def _fill_zeros(self):
        if self.f32_acquirer_institution:
            self.f32_acquirer_institution = self.f32_acquirer_institution.zfill(6)
        if self.f33_agency_code:
            self.f33_agency_code = self.f33_agency_code.zfill(3)
        if self.f37_acquirer_sequence:
            self.f37_acquirer_sequence = self.f37_acquirer_sequence.zfill(12)

    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)
        default['name'] = new_name
        return super(TellerSetting, self).copy(default)
