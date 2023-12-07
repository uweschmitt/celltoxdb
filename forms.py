# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 19:33:29 2020

@author: Alex
"""

from wtforms import Form, StringField, SelectField, DecimalField, SubmitField, \
 IntegerField, BooleanField, SelectMultipleField,validators, FieldList, MultipleFileField, FloatField
 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from app import db
from app.models import Exposure,Cell_line, Endpoint, Solvent,Medium,Person, Institution,Nanomaterial
from wtforms.widgets import html_params
from wtforms_components import FloatIntervalField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import ValidationError

# class RangeWidget(Input):
    
    
#     def __call__(self, field_from,field_to, **kwargs):
#         kwargs.setdefault('id', field.id)
#         kwargs.setdefault('type', self.input_type)
#         if 'value' not in kwargs:
#             kwargs['value'] = field._value()
#         if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
#             kwargs['required'] = True
#         return Markup('<input %s>' % self.html_params(name=field.name, **kwargs))

#     def __call__(self, field, **kwargs):
#         if self.hide_value:
#             kwargs['value'] = ''
#         return super(PasswordInput, self).__call__(field, **kwargs)

# class DecimalNumRangeField(Field):
#     widget = TextInput()
    
#     def _value(self):
#         if self.data:
#             return ', '.join(self.data)
#         else:
#             return ''

#     def process_formdata(self, valuelist):
#         if valuelist:
#             self.data = [x.strip() for x in valuelist[0].split(',')]
#         else:
#             self.data = []


def select_multi_checkbox(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [u'<ul %s style="list-style: none;">' % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<li><input %s /> ' % html_params(**options))
        html.append(u'<label for="%s">%s</label></li>' % (field_id, label))
    html.append(u'</ul>')
    return u''.join(html)

def select_multi_checkbox_dropdown(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [u'<div class="dropdown-checkbox"><button type="button" onclick="toggleDiv(\'%s\')" class="dropbtn">%s</button></div>' % (field_id,field.label)]
    #html = [u'<ul %s style="list-style: none;">' % html_params(id=field_id, class_=ul_class)]
    html.append(u'<div id="%s" class="dropdown-content">' % field_id)
    html.append(u'<ul style="list-style: none;">')
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<li><input %s /> ' % html_params(**options))
        html.append(u'<label for="%s">%s</label>' % (field_id, label))
        html.append(u'<span class="tooltip"><b><i>i</i></b>')
        html.append(u'<span class="tooltiptext">%s</span> </span></li>' % field.description) 
    html.append(u'</ul></div>')
    return u''.join(html)




class SearchForm(FlaskForm):
    chemical_name = StringField('Chemical name', [validators.Optional(),validators.Length(max=40)])
    cas_number = StringField('CAS-Nr.',[validators.Optional(),validators.Length(max=12)])
    
    #endpoint_fields = db.session.query(Endpoint.short_name,Endpoint.full_name).all()
    endpoint_fields = [('AB','metabolic activity (alamarBlue or PrestoBlue)'),
                       ('CF','cell membrane integrity (CFDA-AM)'),
                       ('NR','lysosomal membrane integrity (NeutralRed)')]
    endpoint = SelectMultipleField('Endpoint',[validators.Optional()],
                                   choices = endpoint_fields,
                                   default = [x[0] for x in endpoint_fields],
                                   widget = select_multi_checkbox)
    
    cell_line_fields = db.session.query(Cell_line.short_name,Cell_line.full_name).all()
    cell_line = SelectMultipleField('Cell line',[validators.Optional()],
                                    choices = cell_line_fields,
                                    default = [x[0] for x in cell_line_fields],
                                    widget = select_multi_checkbox)
    #timepoint = IntegerField('Timepoint [h]',[validators.Optional(),validators.NumberRange(min=0,max=10000000)])
    timepoint = SelectField('Timepoint [h]',
                                 [validators.Optional()],
                                   choices = [('all','all'),
                                              ('24','24h'),
                                              ('0','other')
                                              ]
                                 )

    medium = SelectField('Medium',
                                 [validators.Optional()],
                                   choices = [('all','all'),
                                              ('L15/ex','L15/ex'),
                                              ('L15_other','L15 other')
                                              ]
                                 )
    
    
    conc_determination = SelectField('Conc. determination',
                                             [validators.Optional()],
                                             choices = [('all','all'),("me","measured"),("no","nominal")]
                                            )

    logkow_lo = DecimalField("logKow from",[validators.Optional()])
    logkow_hi = DecimalField("logKow to",[validators.Optional()])
    #logkow = DecimalRangeField("logKow",[validators.Optional()])
    min_replicates = IntegerField('Minimum # replicates',[validators.Optional()])
    solvent = StringField('Solvent',[validators.Optional()])
    fbs = SelectField('FBS',[validators.Optional()],
                                 choices = [('all','all'),('1','yes'),('0','no')])
    dosing = SelectMultipleField('Dosing',[validators.Optional()],
                         choices = [("di","direct"),("in","indirect")],
                         default = ["di","in"],
                         widget=select_multi_checkbox)
    passive_dosing = SelectField('Passive dosing',[validators.Optional()],
                                 choices = [('all','all'),('1','yes'),('0','no')])
     
    insert = SelectField('Cell culture insert',[validators.Optional()],choices = [('all','all'),('1','yes'),('0','no')])
    


    
    submit = SubmitField('Filter')

    
class UploadForm(FlaskForm):
    file = FileField()

    @classmethod
    def refresh(self, file=None):
        form = self(file=file)
        return form
    
def get_choices(db,sqla_model):
    fields = db.session.query(sqla_model.id,sqla_model).all()
    fields_str = [(str(k),str(v)) for k,v in fields]
    
   # fields_str.insert(0,('None',''))
    return sorted(fields_str, key=lambda x: x[1])
    



        
import sqlalchemy as sa
import flask_appbuilder
i = sa.inspect(Exposure)

COL_TO_RELOBJ = {}
for k,v in i.relationships.items():
    if(v.direction == sa.orm.interfaces.MANYTOONE):   
        COL_TO_RELOBJ.update({list(v.local_columns)[0].name : v.argument})



COL_TO_FIELD = {
 sa.types.Integer: IntegerField,
 sa.types.Float: FloatField,
 sa.types.String: StringField,
 sa.types.Boolean: BooleanField
 }


def substance_validator(form,field):
    a = form.chemical_id.data == "None"
    b = form.nanomaterial_id.data == "None"
    if ( (a and b) or not (a or b) ):
        raise ValidationError('Either chemical or nanomaterial must be specified.')
        
        
def estimated_validator(form,field):
    fi = form.file.data is None
    print("FILEFIELD HAS VALUE")
    print(form.file.data)
    print(fi)
    ec = form.ec50.data is None
    error = form.error_value.data is None
    rep = form.replicates.data is None
    nconc = form.nconcentrations.data is None
    # ecl = form.ec50_lower.data is None 
    # ecu = form.ec50_upper.data is None 
    b = ec and rep and nconc and error
    print(b)
    print(fi and b)
    print((fi and b) or not (fi or b))
    if ( (fi and b) or not (fi or b) ):
        raise ValidationError('Either a raw file or the EC50 value, including error and number of data points need to be supplied')


    
        

def makeUploadSingleForm(**kwargs):
    """
    

    Parameters
    ----------
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    include_fields = [
        "nanomaterial_id",
        "chemical_id",
        "endpoint_id",
        "cell_line_id",
        "timepoint",
        "medium_id",
        "conc_determination",
        "solvent_id",
        "fbs",
        "dosing",
        "passive_dosing",
        "insert",
        "plate_size",
        "volume",
        "experimenter_id",
        "corresponding_author_id",
        "institution_id",
        "year"
        ]
    
    class UploadSingleForm(FlaskForm):
        @classmethod
        def refresh(self, file=None):
            form = self(file=file)
            return form

    
        
        


    # for fieldName in ["nanomaterial_id","chemical_id"]:
    #     relObj = COL_TO_RELOBJ[fieldName]
    #     choices = get_choices(db,relObj)
    #     field = SelectField(label=label,choices=choices,validators = [validators.Optional(),substance_validator])
    
    for fieldName in include_fields:
        colType = Exposure.__dict__[fieldName].type
        fieldType = COL_TO_FIELD[type(colType)]
        column = Exposure.__dict__[fieldName]
        if "label" in column.info.keys():
            label = column.info['label']
        else:
            label = fieldName
        
        if len(column.foreign_keys) > 0:
            
            relObj = COL_TO_RELOBJ[fieldName]
            # handle the case that relObj is a class resolver and not a class
            if not isinstance(relObj,flask_appbuilder.models.sqla.ModelDeclarativeMeta):
                relObj = relObj()
            choices = get_choices(db,relObj)
            if fieldName == 'chemical_id' or fieldName == 'nanomaterial_id' :
                choices.insert(0,('None',''))
                field = SelectField(label=label,choices=choices,validators = [validators.Optional(),substance_validator])
            else:
                field = SelectField(label=label,choices=choices)
        elif fieldName == "dosing":
            field = SelectField(label=label,choices=[("di","indirect"),("in","direct")])
        elif fieldName == 'conc_determination':
                field = SelectField(label = label,choices = [("no","nominal"),("me","measured")])
        else:
            field = fieldType(label = label)
        
       
        
        setattr(UploadSingleForm,fieldName,field)

    
    setattr(UploadSingleForm,"file",FileField(validators = [validators.Optional(),estimated_validator]))
    setattr(UploadSingleForm,"error_type",
            SelectField(label = "Error type",
                        choices = [("ci","95% Confidence Interval"),('std','Standard Deviation')],
                        validators = [validators.Optional()]))
    setattr(UploadSingleForm,"ec50",
            FloatField(label = 'EC50',
                       validators = [validators.Optional(),estimated_validator]))
    setattr(UploadSingleForm,"error_value",
            FloatField(label = 'Value of error',
                       validators = [validators.Optional(),estimated_validator]))
    setattr(UploadSingleForm,"replicates",
            IntegerField(label = 'number of biological replicates',
                       validators = [validators.Optional(),estimated_validator]))
    setattr(UploadSingleForm,"nconcentrations",
            IntegerField(label = 'number of concentrations tested',
                       validators = [validators.Optional(),estimated_validator]))
    
    return UploadSingleForm(**kwargs)


        
    
# class UploadSingleForm(FlaskForm):
    
#     def __init__(self, *args, **kwargs):
        
#         super(UploadSingleForm, self).__init__(*args, **kwargs)
#         include_fields = [
#             "chemical_id",
#             "nanomaterial_id",
#             "endpoint_id",
#             "cell_line_id",
#             "timepoint",
#             "medium_id",
#             "conc_determination",
#             "solvent_id",
#             "fbs",
#             "dosing",
#             "passive_dosing",
#             "insert",
#             "experimenter_id",
#             "corresponding_author_id",
#             "institution_id",
#             "year"
#             ]
        
#         for fieldName in include_fields:
#             colType = Exposure.__dict__[fieldName].type
#             fieldType = COL_TO_FIELD[type(colType)]
#             column = Exposure.__dict__[fieldName]
#             if "label" in column.info.keys():
#                 label = column.info['label']
#             else:
#                 label = fieldName
            
#             if len(column.foreign_keys) > 0:
                
#                 relObj = COL_TO_RELOBJ[fieldName]
#                 # handle the case that relObj is a class resolver and not a class
#                 if not isinstance(relObj,flask_appbuilder.models.sqla.ModelDeclarativeMeta):
#                     relObj = relObj()
#                 choices = get_choices(db,relObj)
#                 if fieldName == "nanomaterial_id":
#                     field = SelectField(label=label,choices=choices,validators = [validators.Optional()])
#                 else:
#                     field = SelectField(label=label,choices=choices)
#             else:
#                 field = fieldType(label = label)
            
#             tmpfield = self._fields[fieldName] = self.meta.bind_field(self,field,
#                                       {'name': fieldName, 'prefix': self._prefix})
            
#             setattr(self,fieldName,tmpfield)
            
    
            
            
#             #self.add_field(fieldName,fieldName,field)
    
#     file = FileField()

#     @classmethod
#     def refresh(self, file=None):
#         form = self(file=file)
#         return form
        
from app import app
with app.app_context():
    with app.test_request_context('/?file=ssa'):
        af = makeUploadSingleForm()
    # chemical_name = StringField('Chemical name', [validators.Length(max=60)])
    # cas_number = StringField('CAS-Nr.',[validators.Length(max=20)])
    
    # nanomaterial_fields = db.query(Nanomaterial.id,Nanomaterial.__repr__).all()
    # nanomaterial = SelectField("Nanomaterial" ,choices = nanomaterial_fields)
    
    # endpoint_fields = db.session.query(Endpoint.short_name,Endpoint.full_name).all()
    # # endpoint_fields = [('AB','metabolic activity (alamarBlue or PrestoBlue)'),
    # #                    ('CF','cell membrane integrity (CFDA-AM)'),
    # #                    ('NR','lysosomal membrane integrity (NeutralRed)')]
    # endpoint = SelectField('Endpoint',[validators.Optional()],
    #                                choices = endpoint_fields)
    
    # cell_line_fields = db.session.query(Cell_line.short_name,Cell_line.full_name).all()
    # cell_line = SelectField('Cell line', choices = cell_line_fields)
                                   
    # timepoint = IntegerField('Timepoint [h]',[validators.NumberRange(min=0,max=10000000)])


    # medium_fields =  db.session.query(Medium.short_name,Cell_line.full_name).all()
    # medium = SelectField('Medium',choices = medium_fields)
    
    # conc_determination = SelectField('Conc. determination',choices = [("me","measured"),("no","nominal")])

    # solvent_fields =  db.session.query(Solvent.short_name,Solvent.full_name)
    # solvent = StringField('Solvent',choices = solvent_fields)
    # fbs = FloatField('FBS')
    # dosing = SelectField('Dosing',choices = [("di","direct"),("in","indirect")])
    # passive_dosing = BooleanField('Passive dosing')
     
    # insert = BooleanField('Cell culture insert')
    
    # person_list = db.query(Person.short_name,Person.full_name).all()
    # institution_list = db.query(Institution.short_name,Institution.full_name).all()
    
    # cells_seeded = IntegerField("# Cells seeded",validators.Optional())
    # volume = FloatField("Volume in mL",[validators.Optional()])
    
    # experimenter = SelectField("Exprimenter", choices=person_list)
    # principal_investigator = SelectField("Principal Investigator",choices = person_list)
    # year = IntegerField("Year",[validators.NumberRange(min=1900,max=9000)])
    # institution = SelectField("Institution",choices = institution_list)
    # reference = StringField("Publication (DOI)",[validators.Optional()])
    # file = FileField()

    # @classmethod
    # def refresh(self, file=None):
    #     form = self(file=file)
    #     return form



from wtforms_alchemy import ModelForm, ModelFieldList, ModelFormField
from wtforms.fields import FormField
from app.models import Exposure,Chemical,Person,Cell_line,Medium,Endpoint, \
    Institution, Solvent

class ChemicalForm(ModelForm):
    class Meta:
        model = Chemical

class CellLineField(ModelForm):
    class Meta:
        model = Cell_line
    
class MediumForm(ModelForm):
    class Meta:
        model = Medium
        
class PersonForm(ModelForm):
    class Meta:
        model = Person
           
class EndpointForm(ModelForm):
    class Meta:
        model = Endpoint

class SolventForm(ModelForm):
    class Meta:
        model = Solvent

class ExposureForm(ModelForm):
    class Meta:
        model = Exposure
    chemical = ModelFormField(ChemicalForm)
    cell_line = ModelFormField(CellLineField)
    endpoint = ModelFormField(EndpointForm)
    medium = ModelFormField(MediumForm)
    solvent = ModelFormField(SolventForm)
    experimenter = ModelFormField(PersonForm)
    corresponding_author = ModelFormField(PersonForm)
    

