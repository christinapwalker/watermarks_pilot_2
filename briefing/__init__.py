# # __init__.py
#
# from otree.api import (
#     models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c, currency_range
# )
# from django.utils.translation import ugettext_lazy as _
# from django.template.loader import render_to_string
#
# doc = """
# Consent form for the survey.
# """
#
# class Constants(BaseConstants):
#     name_in_url = 'your_app_name'
#     players_per_group = None
#     num_rounds = 1
#     privacy_template = 'your_app_name/PrivacyPolicy.html'  # Path to your privacy template
#
# class Subsession(BaseSubsession):
#     pass
#
# class Group(BaseGroup):
#     pass
#
# class Player(BasePlayer):
#     # button for whether or not they consent
#     consent = models.StringField(
#         choices=[('yes', 'I consent to participate in this study.'), ('no', 'I do not consent to participate in this study.')],
#         widget=widgets.RadioSelect,
#         label=_("Consent to participate in this study")
#     )
#
# # Pages
# from otree.api import Page, WaitPage
#
# class Consent(Page):
#     form_model = 'player'
#     form_fields = ['consent']
#
#     def vars_for_template(player):
#         return {
#             'privacy_template': Constants.privacy_template
#         }
#
#     def before_next_page(player, timeout_happened): # this is from original template, it should return them to prolific, but unclear if it does
#         if player.consent == 'no':
#             player.participant.vars['consent'] = 'no'
#             player.participant.vars['completed'] = True
#             player._payoff = c(0)
#             return
#
#     def is_displayed(player):
#         return not player.participant.vars.get('completed', False)
#
# class Survey(Page):
#     def is_displayed(player):
#         return player.participant.vars.get('consent', '') == 'yes'
#
# class Results(Page):
#     def is_displayed(player):
#         return player.participant.vars.get('consent', '') == 'yes'
#
# page_sequence = [Consent, Survey, Results]
