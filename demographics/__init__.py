# from otree.api import *
#
#
# doc = """
# Collects the demographics/covariates of users
# """
#
#
# class C(BaseConstants):
#     NAME_IN_URL = 'demographics'
#     PLAYERS_PER_GROUP = None
#     NUM_ROUNDS = 1
#
#
# class Subsession(BaseSubsession):
#     pass
#
#
# class Group(BaseGroup):
#     pass
#
#
# # define variables to capture
# class Player(BasePlayer):
#     # bot check
#     bot_check_1 = models.IntegerField(
#         choices=[1,7,3,13,-7],
#         widget=widgets.RadioSelect,
#         label="Please select the number three:")
#     age = models.IntegerField( # age range
#         choices=list(range(18,100)),
#         label="How old are you?"
#     )
#     gender = models.StringField( # gender
#         label="What is your gender?",
#         choices=[
#             [1,'A man'],
#             [2,"A woman"],
#             [3,"Non-binary"],
#             [4,"Another gender"]
#         ]
#     )
#     gender_other = models.StringField( # would like to make this so it only appears if they select option 4 above
#         label='If you selected another gender, please specify:',
#         blank=True,
#         required=None
#     )
#     state = models.StringField( # what state they are from
#         choices=['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
#     'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
#     'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
#     'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
#     'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
#     'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
#     'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
#     'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
#     'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'],
#         label="What state do you live in?",
#         required=None
#     )
#     race = models.StringField( # what is their race
#         choices = ['White/Caucasion', 'African American', 'Hispanic', 'Native American', 'Asian', 'Pacific Islander', 'Other'],
#         label="What is your race?",
#         required=None
#     )
#     race_other = models.StringField( # would like to make this so it only appears if their answer above is other
#         label='If you selected other for race, please specify:',
#         blank=True,
#         required=None
#     )
#     education = models.StringField( # education levels
#         choices=['Less than a high school diploma', 'High school diploma/GED','Some college (no degree)', '2-year college degree','4-year college degree', 'Graduate degree'],
#         widget=widgets.RadioSelect,
#         label="What is the highest level of education that you have completed?",
#         required=None
#     )
#     income = models.StringField( # income levels
#         choices=['$0 - $24,999', '$25,000 - $49,999', '$50,000 - 74,999', '$75,000 - $99,999', '$100,000 - $149,999', '$150,000 - $199,999', '$200,000+'],
#         widget=widgets.RadioSelect,
#         label="What is your combined household income?",
#         required=None
#     )
#     party_id = models.StringField( # party
#         choices=['Democrat', 'Republican', 'Independent', 'Other'],
#         label="Generally speaking, do you think of yourself as a Democrat, as a Republican, an Independent, or something else?",
#         widget=widgets.RadioSelect,
#         required=None
#     )
#     party_id_other = models.StringField( # would like to make this so it only appears if they selected other
#         label='If you selected other for party, please specify:',
#         blank=True,
#         required=None
#     )
#     distinguish_real_ai = models.StringField(
#         label="I feel confident in my ability to distinguish real from AI-generated images.",
#         choices=['True', 'False'],
#         widget=widgets.RadioSelect
#     )
#     trust_smps = models.StringField(
#         label="I generally trust that users on social media platforms will post accurate information.",
#         choices=['True', 'False'],
#         widget=widgets.RadioSelect
#     )
#     trust_execs = models.StringField(
#         label="I trust social media executives to ensure accurate information.",
#         choices=['True', 'False'],
#         widget=widgets.RadioSelect
#     )
#     accuracy_smps = models.StringField(
#         label="I trust the accuracy of content on social media platforms that I use.",
#         choices=['True', 'False'],
#         widget=widgets.RadioSelect
#     )
#
#
#
#
#
#
# # PAGES
# class MyPage(Page):
#     form_model = "player"
#     form_fields = ["bot_check_1","age","gender","gender_other","state","race","race_other","education","income","party_id","party_id_other"]
#
#
#
#
# class ResultsWaitPage(WaitPage):
#     pass
#
#
# class Results(Page):
#     pass
#
#
# page_sequence = [MyPage]
