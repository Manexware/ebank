from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EBankSetting(models.Model):
    _name = 'ebank.setting'
    _description = 'Setting'

    name = fields.Char(required=True)
    ebank_32_acquirer_institution = fields.Char(required=True, size=6)
    ebank_33_agency_code = fields.Char(required=True, size=3)
    ebank_34_cashier = fields.Char(required=True, size=16)
    ebank_37_acquirer_sequence = fields.Char(required=True, size=12)
    ebank_41_terminal = fields.Char(required=True, size=16)

    _order = 'name'

    _sql_constraints = [
        ('name_uk', 'unique(name)', 'Setting must be unique'),
    ]

    @api.constrains('ebank_32_acquirer_institution', 'ebank_33_agency_code', 'ebank_37_acquirer_sequence')
    def _check_num(self):
        if self.ebank_32_acquirer_institution and self.ebank_33_agency_code and self.ebank_37_acquirer_sequence:
            try:
                int(self.ebank_32_acquirer_institution)
            except ValueError:
                raise ValidationError("NAN " + self.ebank_32_acquirer_institution +
                                      " -> " + self._fields['ebank_32_acquirer_institution']._column_string)
            try:
                int(self.ebank_33_agency_code)
            except ValueError:
                raise ValidationError("NAN " + self.ebank_33_agency_code +
                                      " -> " + self._fields['ebank_33_agency_code']._column_string)
            try:
                int(self.ebank_37_acquirer_sequence)
            except ValueError:
                raise ValidationError("NAN " + self.ebank_37_acquirer_sequence +
                                      " -> " + self._fields['ebank_37_acquirer_sequence']._column_string)

    @api.constrains('ebank_34_cashier', 'ebank_41_terminal')
    def _check_al_num(self):
        if self.ebank_34_cashier:
            if not self.ebank_34_cashier.isalnum():
                raise ValidationError("NAALN " + self.ebank_34_cashier +
                                      " -> " + self._fields['ebank_34_cashier']._column_string)
        if self.ebank_41_terminal:
            if not self.ebank_41_terminal.isalnum():
                raise ValidationError("NAALN " + self.ebank_41_terminal +
                                      " -> " + self._fields['ebank_41_terminal']._column_string)

    @api.onchange('ebank_32_acquirer_institution', 'ebank_33_agency_code', 'ebank_37_acquirer_sequence')
    def _fill_zeros(self):
        if self.ebank_32_acquirer_institution:
            self.ebank_32_acquirer_institution = self.ebank_32_acquirer_institution.zfill(6)
        if self.ebank_33_agency_code:
            self.ebank_33_agency_code = self.ebank_33_agency_code.zfill(3)
        if self.ebank_37_acquirer_sequence:
            self.ebank_37_acquirer_sequence = self.ebank_37_acquirer_sequence.zfill(12)

    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)
        default['name'] = new_name
        return super(EBankSetting, self).copy(default)
