from openerp import models, fields, api
from openerp.exceptions import ValidationError


class EbSetting(models.Model):
    _name = 'eb.setting'
    _description = 'Setting'

    name = fields.Char(required=True)
    eb_32_acquirer_institution = fields.Char(required=True, size=6)
    eb_33_agency_code = fields.Char(required=True, size=3)
    eb_34_cashier = fields.Char(required=True, size=16)
    eb_37_acquirer_sequence = fields.Char(required=True, size=12)
    eb_41_terminal = fields.Char(required=True, size=16)

    _order = 'name'

    _sql_constraints = [
        ('name_uk', 'unique(name)', 'Setting must be unique'),
    ]

    @api.one
    @api.constrains('eb_32_acquirer_institution','eb_33_agency_code','eb_37_acquirer_sequence')
    def _check_num(self):
        if self.eb_32_acquirer_institution and self.eb_33_agency_code and self.eb_37_acquirer_sequence:
            try:
                int(self.eb_32_acquirer_institution)
            except ValueError:
                raise ValidationError("NAN " + self.eb_32_acquirer_institution +
                                      " -> " + self._fields['eb_32_acquirer_institution']._column_string)
            try:
                int(self.eb_33_agency_code)
            except ValueError:
                raise ValidationError("NAN " + self.eb_33_agency_code +
                                      " -> " + self._fields['eb_33_agency_code']._column_string)
            try:
                int(self.eb_37_acquirer_sequence)
            except ValueError:
                raise ValidationError("NAN " + self.eb_37_acquirer_sequence +
                                      " -> " + self._fields['eb_37_acquirer_sequence']._column_string)

    @api.one
    @api.constrains('eb_34_cashier','eb_41_terminal')
    def _check_al_num(self):
        if self.eb_34_cashier:
            if not self.eb_34_cashier.isalnum():
                raise ValidationError("NAALN " + self.eb_34_cashier +
                                      " -> " + self._fields['eb_34_cashier']._column_string)
        if self.eb_41_terminal:
            if not self.eb_41_terminal.isalnum():
                raise ValidationError("NAALN " + self.eb_41_terminal +
                                      " -> " + self._fields['eb_41_terminal']._column_string)

    @api.one
    @api.onchange('eb_32_acquirer_institution','eb_33_agency_code','eb_37_acquirer_sequence')
    def _fill_zeros(self):
        if self.eb_32_acquirer_institution:
            self.eb_32_acquirer_institution = self.eb_32_acquirer_institution.zfill(6)
        if self.eb_33_agency_code:
            self.eb_33_agency_code = self.eb_33_agency_code.zfill(3)
        if self.eb_37_acquirer_sequence:
            self.eb_37_acquirer_sequence = self.eb_37_acquirer_sequence.zfill(12)

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
        return super(EbSetting, self).copy(default)
