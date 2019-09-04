from django import forms


# Add your forms here
from drchrono.options import GENDERS, RACE, ETHNICITY, LANGUAGES, STATES


class PatientCheckInForm(forms.Form):

    first_name = forms.CharField(label='First Name', max_length=200)
    last_name = forms.CharField(label='Last Name', max_length=200)
    social_security_number = forms.CharField(label='Social Security Number', max_length=11, required=True)


class DemographicsForm(forms.Form):
    doctor = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(label='First Name', max_length=100)
    middle_name = forms.CharField(label='Middle Name', max_length=100, required=False)
    last_name = forms.CharField(label='Last Name', max_length=100)
    nick_name = forms.CharField(label='Nick Name', max_length=100, required=False)
    date_of_birth = forms.DateField(label='Date of Birth')
    gender = forms.ChoiceField(label='Gender', choices=GENDERS)
    social_security_number = forms.CharField(label='Social Security Number', max_length=11, required=False)
    race = forms.ChoiceField(label='Race', choices=RACE, required=False)
    ethnicity = forms.ChoiceField(label='Ethnicity', choices=ETHNICITY, required=False)
    preferred_language = forms.ChoiceField(label='Preferred Language', choices=LANGUAGES, required=False)
    home_phone = forms.CharField(label='Home Phone', max_length=15, required=False)
    cell_phone = forms.CharField(label='Cell Phone', max_length=15, required=False)
    office_phone = forms.CharField(label='Work Phone', max_length=15, required=False)
    email = forms.EmailField(label='Email', required=False)
    address = forms.CharField(label='Address', max_length=100, required=False)
    city = forms.CharField(label='City', max_length=100, required=False)
    state = forms.ChoiceField(label='State', choices=STATES, required=False)
    zip_code = forms.CharField(label='Zip Code', max_length=5, required=False)
    emergency_contact_name = forms.CharField(label='Emergency Contact Name', max_length=255, required=False)
    emergency_contact_phone = forms.CharField(label='Emergency Conatct Phone', max_length=15, required=False)
    emergency_contact_relation = forms.CharField(label='Emergency Contact Relation', max_length=100, required=False)
    employer = forms.CharField(label='Employer', max_length=255, required=False)
    employer_address = forms.CharField(label='Employer Address', max_length=100, required=False)
    employer_city = forms.CharField(label='Employer City', max_length=100, required=False)
    employer_state = forms.ChoiceField(label='Employer State', choices=STATES, required=False)
    employer_zip_code = forms.CharField(label='Emplyer Zip Code', max_length=5, required=False)
    primary_care_physician = forms.CharField(label='Primary Care Physician', max_length=255, required=False)
    responsible_party_name = forms.CharField(label='Responsible Party Name', max_length=255, required=False)
    responsible_party_relation = forms.CharField(label='Responsible Party Relation', max_length=100, required=False)
    responsible_party_phone = forms.CharField(label='Responsible Party Phone', max_length=15, required=False)
    responsible_party_email = forms.EmailField(label='Responsible Party Email', required=False)


